import sublime, sublime_plugin
import SublimeHints
import hints
import textwrap

class DoubleViewHintsCommand(SublimeHints.HintsRenderer):
    
    def render(self, hints_file):
        self.hints_file = hints_file
        self.separator = 0.7
        self.text_view = self.view
        self.hint_view = self.__create_double_view__(self.separator)
        self.__calculate_dimensions__()
        self.__generate_hints_view__()
        self.__highlight_text__()
        self.__setup_views__()
        
        

    def __create_double_view__(self, separator):
        self.view.window().run_command("set_layout", {"cols": [0.0, separator, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
        self.view.settings().set('word_wrap', False)
        new_file = self.view.window().new_file()
        new_file.set_scratch(True)
        new_file.settings().set('word_wrap', True)
        #new_file.settings().set( "line_numbers", False)
        #new_file.settings().set( "gutter", False)
        #new_file.settings().set( "show_minimap", False)
        #new_file.settings().set( "overlay_scroll_bars", "disabled")
        new_file.window().run_command("move_to_group", { "group": 1 } )
        return new_file

    def __setup_views__(self):
        self.hint_view.set_read_only(True)
        self.hint_view.settings().set('word_wrap', False)

    def __calculate_dimensions__(self):
        w, h = self.hint_view.viewport_extent()
        self.hint_view_width = w//self.view.em_width()
        self.view_height, _ = self.text_view.rowcol(self.text_view.size())


    def __generate_hints_view__(self):
        self.hints = self.__create_single_region_hints__()
        edit = self.hint_view.begin_edit()
        try:
            current = 0
            for i, hint in enumerate(self.hints):
                #self.hint_view.insert(edit, self.hint_view.size(), self.__format_hint__(hint, i + 1))
                formatted = self.__format_hint__(hint, i + 1)
                wrapped = textwrap.wrap(formatted, width = self.hint_view_width)
                height = len(wrapped)
                begin, _ = self.text_view.rowcol(hint.text_place.begin())
                print current, begin, height
                if current >= begin:
                    for line in wrapped:
                        self.hint_view.insert(edit, self.hint_view.size(), line + "\n")
                    current += height
                else:
                    for i in range(0, begin - current):
                        self.hint_view.insert(edit, self.hint_view.size(), "\n")
                    for line in wrapped:
                        self.hint_view.insert(edit, self.hint_view.size(), line + "\n")
                    current = begin + height
        finally:
            self.hint_view.end_edit(edit)

    def __highlight_text__(self):
        self.text_view.add_regions("text_highlight", map(lambda x: x.text_place, self.hints), "comment", "bookmark")

    def __create_single_region_hints__(self):
        single_hints = []
        for hint in self.hints_file.hints:
            for i, place in enumerate(hint.places):
                single_hints.append(DoubleViewHint(hint, i))
        single_hints.sort(None, lambda x: x.text_place.begin())
        return single_hints


    def __format_hint__(self, hint, number):
        return "{0}. {1}\n".format(number, hint.text)




class DoubleViewHint(object):
    def __init__(self, hint, number, hint_place=None):
        self.hint = hint
        self.text = hint.text
        self.text_place = hint.places[number]
        self.hint_place = hint_place