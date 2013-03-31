import sublime, sublime_plugin
import SublimeHints
import hints

class DoubleViewHintsCommand(SublimeHints.HintsRenderer):
    
    def render(self, hints_file):
        self.hints_file = hints_file
        self.separator = 0.7
        self.text_view = self.view
        self.hint_view = self.__create_double_view__(self.separator)
        self.__generate_hints_view__()
        self.hint_view.set_read_only(True)
        

    def __create_double_view__(self, separator):
        self.view.window().run_command("set_layout", {"cols": [0.0, separator, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
        new_file = self.view.window().new_file()
        new_file.set_scratch(True)
        new_file.window().run_command("move_to_group", { "group": 1 } )
        return new_file


    def __generate_hints_view__(self):
        self.single_hints = self.__create_single_region_hints__()
        edit = self.hint_view.begin_edit()
        try:
            for hint in self.single_hints:
                self.hint_view.insert(edit, self.hint_view.size(), self.__format_hint__(hint))
        finally:
            self.hint_view.end_edit(edit)

    def __create_single_region_hints__(self):
        single_hints = []
        for hint in self.hints_file.hints:
            for place in hint.places:
                single_hints.append(hints.Hint(hint.text, [place]))
        single_hints.sort(None, lambda x: x.places[0].begin())
        return single_hints


    def __format_hint__(self, hint):
        return hint.text + "\n"