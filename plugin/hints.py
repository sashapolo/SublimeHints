"""
Hints object internal representation.
"""
import json
from datetime import datetime
import functools
import copy
import os
import sublime

ISO8601_DATE_FORMAT = '%Y-%m-%d:%H:%M:%S'


class HintFormatError(Exception):
    pass


class HintsFileNotFoundError(Exception):
    pass


class SourceFileNotFoundError(Exception):
    pass


class Hint(object):
    def __init__(self, text, places = [], tags = []):
        self.text = text
        self.places = places
        self.tags = tags

    @classmethod
    def from_json(cls, view, json_obj):
        def list_to_region(lst):
            begin_line = view.line(view.text_point(lst[0], 0))
            if lst[1] > begin_line.size():
                lst[1] = begin_line.size()
            end_line = view.line(view.text_point(lst[2], 0))
            if lst[3] > end_line.size():
                lst[3] = end_line.size()
            return sublime.Region(view.text_point(lst[0], lst[1]), view.text_point(lst[2], lst[3]))

        if 'text' not in json_obj:
            raise HintFormatError('Illegal hint format: Field `text` is missing')
        text = json_obj.pop('text')
        if 'places' not in json_obj:
            raise HintFormatError('Illegal hint format: Field `places` is missing')
        places = json_obj.pop('places')
        try:
            places = map(list_to_region, places)
        except (TypeError, IndexError):
            raise HintFormatError('Illegal places format %s' % places)
        tags = []
        if 'tags' in json_obj:
            tags = json_obj.pop('tags')
        if json_obj:
            raise HintFormatError('Illegal hint format: unknown fields: %s' % json_obj)
        return cls(text, places, tags)

    def to_json(self, view):
        def region_to_list(region):
            return list(view.rowcol(region.begin())) + list(view.rowcol(region.end()))

        if not self.tags:
            return {'text': self.text, 'places': map(region_to_list, self.places)}
        else:
            return {'text': self.text, 'places': map(region_to_list, self.places), 'tags': self.tags}

    def __str__(self):
        return u'<Hint: places=%(places)s text="%(text)s">' % self.__dict__


class Meta(object):

    def __init__(self,
                 created = None,
                 modified = None,
                 author = 'unknown',
                 createdWith = 'unknown',
                 createdTimestamp = None,
                 modifiedTimestamp = None,
                 md5sum = None,
                 **kwargs):
        self.created = created
        self.modified = modified
        self.author = author
        self.md5sum = md5sum
        self.createdTimestamp = createdTimestamp
        self.modifiedTimestamp = modifiedTimestamp
        # if kwargs:
        #     raise HintFormatError('Unknown fields: %s' % kwargs)
        self.__dict__.update(kwargs)

    @classmethod
    def from_json(cls, json_obj):
        for timestamp in ('created', 'updated', 'createdTimestamp', 'modifiedTimestamp'):
            if timestamp in json_obj:
                try:
                    json_obj[timestamp] = datetime.strptime(json_obj[timestamp], ISO8601_DATE_FORMAT)
                except ValueError:
                    raise HintFormatError('Illegal time format: %s' % timestamp)
        return cls(**json_obj)

    def to_json(self, file_name):
        result = copy.deepcopy(dict((k, v) for k, v in self.__dict__.items() if v is not None))
        if self.created:
            result["created"] = self.created.strftime(ISO8601_DATE_FORMAT)
        if self.modified:
            result["modified"] = self.modified.strftime(ISO8601_DATE_FORMAT)
        if self.createdTimestamp:
            result["createdTimestamp"] = self.createdTimestamp.strftime(ISO8601_DATE_FORMAT)
        if self.modifiedTimestamp:
            result["modifiedTimestamp"] = self.modifiedTimestamp.strftime(ISO8601_DATE_FORMAT)
        return result

    def __str__(self):
        return u'<Meta:' + u' '.join('%s=%s' % (k, v) for k, v in self.__dict__.items()) + u'>'


class HintFile(object):
    def __init__(self, meta, hints, file_name):
        self.meta = meta
        self.hints = hints
        self.name = file_name

    @classmethod
    def load_json(cls, view, json_file_name):
        with open(json_file_name, 'r') as hints_file:
            json_obj = json.load(hints_file)
            if 'hints' not in json_obj:
                raise HintFormatError('Illegal hint file format: field `hints` is missing')
            partial_from_json = functools.partial(Hint.from_json, view)
            hints = map(partial_from_json, json_obj.pop('hints'))
            meta = Meta.from_json(json_obj)
            return cls(meta, hints, json_file_name)

    def dump_json(self, view):
        with open(self.name, 'w') as hints_file:
            source_file_name = os.path.splitext(self.name)[0]
            if not os.path.exists(source_file_name):
                raise SourceFileNotFoundError("File %s not found" % source_file_name)
            self.meta.modified = datetime.fromtimestamp(os.path.getmtime(self.name))
            json_obj = self.meta.to_json(source_file_name)
            json_obj["hints"] = []
            for hint in self.hints:
                json_obj["hints"].append(hint.to_json(view))
            json.dump(json_obj, hints_file, indent = 4)

    def __str__(self):
        string =  u'<Hint file for %s (hash=%s)>' % (self.name, self.meta.md5sum)
        return string.encode('utf-8')
