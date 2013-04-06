'''
Created on Mar 17, 2013

@author: snowball
'''

from SublimeHints import HintsRenderer
from hint_editor.highlighter import HintsHighlighter
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


class BeginEditHintsCommand(HintsRenderer):
    _regions_key = "editor"

    @classmethod
    def get_regions_key(self):
        return self._regions_key

    def render(self, hints_file):
        self.hints = hints_file.hints
        self.set_layout()
        self.print_hints()

    def set_layout(self):
        self.view.window().run_command('set_layout',
                                       { "cols":  [0.0, 0.5, 1.0],
                                         "rows":  [0.0, 1.0],
                                         "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
                                       })

    def create_hint_view(self):
        result = self.view.window().new_file()
        result.window().run_command('move_to_group', {"group": 1})
        return result

    def print_hints(self):
        displayed_hints = set()
        hint_counter = 0
        # this piece of code is fucked up
        for region in self.view.sel():
            for hint in self.hints:
                if hint not in displayed_hints:
                    for hint_region in hint.places:
                        if hint_region.intersects(region):
                            hint_view = self.create_hint_view()
                            hint_counter += 1
                            hint_view.set_name("Hint " + str(hint_counter))
                            self.print_hint(hint_view, hint)
                            displayed_hints.add(hint)
                            break

        highlighter = HintsHighlighter(self.view, displayed_hints)
        highlighter.highlight_hints(self._regions_key, "string")

    def print_hint(self, view, hint):
        edit = view.begin_edit()
        try:
            view.insert(edit, view.size(), hint.text)
        finally:
            view.end_edit(edit)


class StopEditHintsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        highlighter = HintsHighlighter(self.view)
        highlighter.unhighlight_hints(BeginEditHintsCommand.get_regions_key())
        self.view.window().run_command('set_layout',
                                       { "cols":  [0.0, 1.0],
                                         "rows":  [0.0, 1.0],
                                         "cells": [[0, 0, 1, 1]]
                                       })
        self.view.set_scratch(True)

