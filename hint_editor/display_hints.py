'''
Created on Mar 17, 2013

@author: snowball
'''

from SublimeHints import HintsRenderer
from hint_editor.HintsHighlighter import HintsHighlighter
import sublime_plugin

class HighlightHintsCommand(HintsRenderer):
    _regions_key = "highlighter"
    _highlighted_views = {}

    @classmethod
    def get_regions_key(self):
        return self._regions_key

    def render(self, hints_file):
        highlighted = self._highlighted_views.setdefault(self.view.id, False)
        highlighter = HintsHighlighter(self.view, hints_file.hints)
        if not highlighted:
            highlighter.highlight_hints(self._regions_key, "comment")
            self._highlighted_views[self.view.id] = True
        else:
            highlighter.unhighlight_hints(self._regions_key)
            self._highlighted_views[self.view.id] = False


class DisplaySelectedHintsCommand(HintsRenderer):
    _regions_key = "selecter"

    @classmethod
    def get_regions_key(self):
        return self._regions_key

    def render(self, hints_file):
        self.hints = hints_file.hints
        if self.view.window().num_groups() == 1:
            self.hint_view = self.create_hints_view()
        self.hint_view.window().run_command('move_to_group', {"group": 1})
        edit = self.hint_view.begin_edit()
        try:
            self.print_hints(edit)
        finally:
            self.hint_view.end_edit(edit)

    def create_hints_view(self):
        self.view.window().run_command('set_layout',
                                       { "cols":  [0.0, 0.5, 1.0],
                                         "rows":  [0.0, 1.0],
                                         "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
                                       })
        return self.view.window().new_file()

    def print_hints(self, edit):
        self.hint_view.insert(edit, self.hint_view.size(), self.view.file_name() + ":\n")
        displayed_hints = set()
        # this piece of code is fucked up
        for region in self.view.sel():
            for hint in self.hints:
                if hint not in displayed_hints:
                    for hint_region in hint.places:
                        if hint_region.intersects(region):
                            self.print_hint(hint, edit)
                            displayed_hints.add(hint)
                            break

        highlighter = HintsHighlighter(self.view, displayed_hints)
        highlighter.highlight_hints(self._regions_key, "string")

    def print_hint(self, hint, edit):
        self.hint_view.insert(edit, self.hint_view.size(), "=" * 8 + " Hint " + "=" * 8 + "\n")
        self.hint_view.insert(edit, self.hint_view.size(), self.format_hint(hint))

    def format_hint(self, hint):
        result = ""
        for region in hint.places:
            result += self.format_rowcol(*self.view.rowcol(region.begin())) + " -- "
            result += self.format_rowcol(*self.view.rowcol(region.end())) + "\n"
        return result + "\n" + hint.text + "\n\n"

    def format_rowcol(self, row, col):
        return "(line " + str(row + 1) + ", col " + str(col + 1) + ")"


# NOTE: this command works really badly, so consider it experimental
class ClearEditSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        highlighter = HintsHighlighter(self.view)
        highlighter.unhighlight_hints(DisplaySelectedHintsCommand.get_regions_key())
        self.view.window().run_command('set_layout',
                                       { "cols":  [0.0, 1.0],
                                         "rows":  [0.0, 1.0],
                                         "cells": [[0, 0, 1, 1]]
                                       })
