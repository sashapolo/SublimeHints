"""
Hints object internal representation.
"""
import json
from datetime import datetime
import functools
import sublime

ISO8601_DATE_FORMAT = '%Y-%m-%d'


class HintFormatError(Exception):
    pass


class HintsFileNotFoundError(Exception):
    pass


class Hint(object):
    def __init__(self, text, places):
        self.text = text
        self.places = places

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
        if json_obj:
            raise HintFormatError('Illegal hint format: unknown fields: %s' % json_obj)
        return cls(text, places)

    def __str__(self):
        return '<Hint: places=%(places)s text="%(text)s">' % self.__dict__


class Meta(object):

    def __init__(self, created=None, updated=None, author='unknown', md5sum=None, file=None, **kwargs):
        self.created = created
        self.updated = updated
        self.author = author
        self.md5sum = md5sum
        self.file = file
        # if kwargs:
        #     raise HintFormatError('Unknown fields: %s' % kwargs)
        self.__dict__.update(kwargs)

    @classmethod
    def from_json(cls, json_obj):
        for timestamp in ('created', 'updated'):
            if timestamp in json_obj:
                try:
                    json_obj[timestamp] = datetime.strptime(json_obj[timestamp], ISO8601_DATE_FORMAT)
                except ValueError:
                    raise HintFormatError('Illegal time format: %s' % timestamp)
        return cls(**json_obj)

    def __str__(self):
        return '<Meta:' + ' '.join('%s=%s' % (k, v) for k, v in self.__dict__.items()) + '>'

class HintFile(object):
    def __init__(self, meta, hints):
        self.meta = meta
        self.hints = hints

    @classmethod
    def load_json(cls, view, json_file_name):
        with open(json_file_name, 'r') as hints_file:
            json_obj = json.load(hints_file)
            if 'hints' not in json_obj:
                raise HintFormatError('Illegal hint file format: field `hints` is missing')
            partial_from_json = functools.partial(Hint.from_json, view)
            hints = map(partial_from_json, json_obj.pop('hints'))
            meta = Meta.from_json(json_obj)
            return cls(meta, hints)

    def __str__(self):
        return '<Hint file for %s (hash=%s)>' % (self.meta.file, self.meta.md5sum)


