import sublime
import SublimeHints
import textwrap
import synchro
import arrow
import string


class DoubleViewHintsCommand(SublimeHints.HintsRenderer):

    activated = {}
    activate_listener = False

    def render(self, hints_file, **kwargs):
        id = self.view.id()
        #print id
        for key in DoubleViewHintsCommand.activated:
            if id in key:
                self.__deactivate(DoubleViewHintsCommand.activated[key])
                del DoubleViewHintsCommand.activated[key]
                break
        else:
            self.__activate(hints_file, **kwargs)

    def __deactivate(self, command):
        target_file = command.text_view
        hint_file = command.hint_view.view
        synchronizer = command.synchro
        views_id = map(lambda x: x.id(), target_file.window().views())
        if hint_file.id() in views_id:
            target_file.window().focus_view(hint_file)
            target_file.window().run_command("close_file")
        target_file.erase_regions("text_highlight")
        if len(DoubleViewHintsCommand.activated) == 1:
            target_file.window().run_command("set_layout",
                                            {"cols": [0.0, 1.0],
                                             "rows": [0.0, 1.0],
                                             "cells": [[0, 0, 1, 1]]})
            DoubleViewHintsCommand.activate_listener = False
        synchronizer.remove_view(target_file)
        synchronizer.remove_view(hint_file)
        target_file.window().focus_view(target_file)

    def __activate(self, hints_file, **kwargs):
        if "tags" in kwargs:
            tags = kwargs["tags"]
        self.hints_file = hints_file
        self.separator = 0.6
        self.text_view = self.view
        self.hint_view = self.__create_double_view__(self.separator)
        self.hint_view_width = self.__calculate_width__(self.hint_view)
        self.hint_view_height = self.__calculate_height__()
        tags = []
        if "tags" in kwargs:
            tags = kwargs["tags"]
        self.hint_view = HintView(self.hint_view, self._filter_hints(tags),
                                  self.text_view, self.hint_view_height,
                                  width = self.hint_view_width)
        #self.__highlight_text__()
        self.__setup_views__()
        self.__add_activated()

    def __create_double_view__(self, separator):
        self.view.settings().set('word_wrap', False)
        self.view.window().run_command("set_layout",
                                      {"cols": [0.0, separator, 1.0],
                                       "rows": [0.0, 1.0],
                                       "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
        new_file = self.view.window().new_file()
        new_file.set_name("Hints")
        new_file.set_scratch(True)
        new_file.settings().set('word_wrap', False)
        new_file.settings().set('margin', 0)
        new_file.window().run_command("move_to_group", {"group": 1})
        return new_file

    def __calculate_width__(self, view):
        w, h = view.viewport_extent()
        return w//view.em_width()

    def __calculate_height__(self):
        return self.file_content().count("\n")

    def __highlight_text__(self):
        self.text_view.add_regions("text_highlight",
                map(lambda x: x.text_place, self.hint_view.get_hints()), "comment", "bookmark")

    def __setup_views__(self):
        self.synchro = synchro.Synchronizer(self.text_view, self.hint_view.view)
        self.synchro.run()
        self.view.window().focus_view(self.view)

    def _filter_hints(self, tags):
        if not tags:
            return self.hints_file.hints
        else:
            hints = self.hints_file.hints
            for tag in tags:
                hints = filter(lambda x: tag in x.tags, hints)
            return hints

    def __add_activated(self):
        key = (self.text_view.id(), self.hint_view.view.id())
        DoubleViewHintsCommand.activated[key] = self
        DoubleViewHintsCommand.activate_listener = True
        #print DoubleViewHintsCommand.activated.keys()

    def __find_hint_repr(self, line):
        for hint in self.hint_view.hints:
            if (line >= hint.begin_line) and \
               (line <= (hint.begin_line + hint.height - 1)):
                return hint

    def reload_hint_file(self):
        self.hints_file = super(DoubleViewHintsCommand, self).load_file()
        self.hint_view.reload(self.hints_file.hints)

    def hints_in_region_repr(self, region):
        hint_view = self.hint_view.view
        lines = hint_view.lines(region)
        line_numbers = map(lambda x: (hint_view.rowcol(x.begin()))[0], lines)
        hints_set = set()
        for line_number in line_numbers:
            hint = self.__find_hint_repr(line_number)
            if hint is not None:
                hints_set.add(hint)
        return list(hints_set)

    def hints_in_region(self, region):
        return map(lambda x: x.hint, self.hints_in_region_repr(region))

    @classmethod
    def find_by_target_view_id(cls, id):
        for key in cls.activated:
            if key[0] == id:
                return cls.activated[key]
                break
        else:
            return None

    @classmethod
    def find_by_hint_view_id(cls, id):
        for key in cls.activated:
            if key[1] == id:
                return cls.activated[key]
                break
        else:
            return None


class HintRepr(object):
    def __init__(self, hint, number = 0, width = 80):
        self.hint = hint
        self.text = hint.text
        self.text_place = hint.places[number]
        self.tags = hint.tags
        self.formatted = None
        self.width = width
        self.height = None
        self.begin_line = None
        self.format_hint()

    def format_hint(self, number = None, with_tags = True):
        if with_tags:
            if number is None:
                self.formatted = self._format_tags() + self.text
            else:
                self.formatted = u"{0}. {1}{2}\n".format(number, self._format_tags(), self.text)
        else:
            if number is None:
                self.formatted = self.text
            else:
                self.formatted = u"{0}. {2}\n".format(number, self.text)
        self.formatted = textwrap.fill(self.formatted, width = self.width, replace_whitespace=False)
        self.formatted += "\n"
        self.height = self.formatted.count("\n")
        return self.formatted

    def _format_tags(self):
        string = u"Tags: "
        if not self.tags:
            return "";
        else:
            for i, tag in enumerate(self.tags):
                if i == 0:
                    string = string + tag
                else:
                    string = string + ", " + tag
            return string + "\nText: "

    def __str__(self):
        return self.formatted


class HintPanel(object):
    def __init__(self, hints, text_view, width = 80, with_tags = True):
        self.hints_repr = []
        self.arrows = []
        for hint in hints:
            for i, place in enumerate(hint.places):
                self.hints_repr.append(HintRepr(hint, number = i, width = width))
        self.hints_repr.sort(None, lambda x: x.text_place.begin())
        self.with_tags = with_tags
        self.content = self.__form_content__(text_view)

    def __form_content__(self, text_view):
        current = 0
        content = str()
        for i, hint in enumerate(self.hints_repr):
            formatted = hint.format_hint(i + 1, self.with_tags)
            height = hint.height
            begin, _ = text_view.rowcol(hint.text_place.begin())
            if current >= begin:
                self.arrows.append(arrow.Arrow(begin, current))
                hint.begin_line = current
                content += formatted
                current += height
            else:
                self.arrows.append(arrow.Arrow(begin, begin))
                hint.begin_line = begin
                content += "\n" * (begin - current)
                content += formatted
                current = begin + height
        return content

    def get_content(self):
        return self.content

    def content_height(self):
        return self.content.count("\n")

    def get_arrows(self):
        return self.arrows


class HintView(object):
    def __init__(self, view, hints, text_view, height, width = 80):
        self.view = view
        self.text_view = text_view
        self.height = height
        self.width = width
        self.hint_panel = HintPanel(hints, text_view, width)
        self.arrow_panel = arrow.ArrowPanel(self.hint_panel.get_arrows(), self.hint_panel.content_height())
        self.hints = self.hint_panel.hints_repr
        self.content = self.__form_content__()
        self.view.set_read_only(False)
        edit = self.view.begin_edit()
        try:
            self.view.erase(edit, sublime.Region(0, self.view.size()))
            self.view.insert(edit, 0, self.content)
        finally:
            self.view.end_edit(edit)
        self.view.set_read_only(True)

    def __form_content__(self):
        hint_content = self.hint_panel.get_content().splitlines()
        arrow_content = self.arrow_panel.get_content().splitlines()
        content = []
        for i in range(len(hint_content)):
            if len(arrow_content) <= i:
                arrow_string = " " * self.arrow_panel.width
            else:
                arrow_string = arrow_content[i]
            hint_string = hint_content[i]
            content.append(arrow_string + " " + hint_string)
        content = string.join(content, "\n")
        if self.height > self.hint_panel.content_height():
            content += "\n" * (self.height - self.hint_panel.content_height())
        return content

    def get_hints(self):
        return self.hint_panel.hints_repr

    def reload(self, hints):
        self.__init__(self.view, hints, self.text_view, self.height, self.width)
