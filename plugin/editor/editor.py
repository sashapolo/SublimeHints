'''
Created on Mar 17, 2013

@author: snowball
'''

from SublimeHints import HintsRenderer
from highlighter import HintsHighlighter
from hints import Meta, HintFile
import sublime_plugin
import sublime
import os
from datetime import datetime
import hashlib


displayed_hints = {}


class BeginEditHintsCommand(HintsRenderer):
    _regions_key = "editor"

    @classmethod
    def get_regions_key(cls):
        return cls._regions_key

    def render(self, hints_file):
        self.hints_file = hints_file
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
        def print_hint(view, hint):
            edit = view.begin_edit()
            try:
                view.insert(edit, view.size(), hint.text)
            finally:
                view.end_edit(edit)

        hint_set = set()
        hint_counter = 0
        # this piece of code is fucked up
        for region in self.view.sel():
            for hint in self.hints:
                if hint not in hint_set:
                    for hint_region in hint.places:
                        if hint_region.intersects(region):
                            hint_view = self.create_hint_view()
                            hint_view.set_scratch(True)
                            hint_view.set_scratch(False)
                            hint_counter += 1
                            hint_view.set_name("Hint " + str(hint_counter))
                            print_hint(hint_view, hint)
                            hint_set.add(hint)
                            displayed_hints[hint_view.id()] = { "file": self.hints_file,
                                                                "hint": hint,
                                                                "parent_view": self.view
                                                              }
                            break

        highlighter = HintsHighlighter(self.view, hint_set)
        highlighter.highlight_hints(self._regions_key, "string")


class StopEditHintsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        id = self.view.id()
        if id in displayed_hints:
            hints_file = displayed_hints[id]["file"]
            hint = displayed_hints[id]["hint"]
            parent_view = displayed_hints[id]["parent_view"]

            hint.text = self.view.substr(sublime.Region(0, self.view.size()))
            hints_file.dump_json(parent_view)
            self.view.set_scratch(True)
            self.view.window().run_command("close_file")

            del displayed_hints[id]
            if not displayed_hints:
                highlighter = HintsHighlighter(parent_view)
                highlighter.unhighlight_hints(BeginEditHintsCommand.get_regions_key())


class CreateNewHintsFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.hints_file_name = self.view.file_name() + ".hints"
        if os.path.exists(self.hints_file_name):
            sublime.status_message("Error: file %s already exists" % self.hints_file_name)
            return
        self.view.window().show_input_panel("Author:", "", self.on_done, None, None)

    def on_done(self, user_input):
        with open(self.hints_file_name, "w"):
            source_file_name = self.view.file_name()
            meta = Meta(created = datetime.fromtimestamp(os.path.getctime(self.hints_file_name)),
                        modified = datetime.fromtimestamp(os.path.getmtime(self.hints_file_name)),
                        author = user_input,
                        createdWith = "SublimeHints editor v0.1",
                        createdTimestamp = datetime.fromtimestamp(os.path.getctime(source_file_name)),
                        modifiedTimestamp = datetime.fromtimestamp(os.path.getmtime(source_file_name)),
                        md5sum = hashlib.md5(open(source_file_name, 'rb').read()).hexdigest())
            hint_file = HintFile(meta, [], self.hints_file_name)
            hint_file.dump_json(self.view)
