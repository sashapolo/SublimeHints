'''
Created on Mar 17, 2013

@author: snowball
'''

from SublimeHints import HintsRenderer
from hints import Meta, HintFile, Hint
from viewers.double_view import DoubleViewHintsCommand
from datetime import datetime
import sublime_plugin
import sublime
import os
import hashlib


_displayed_hints = {}
_edit_all = False


class BeginEditHintsCommand(HintsRenderer):

    def render(self, hints_file, **kwargs):
        double_view = DoubleViewHintsCommand.find_by_hint_view_id(self.view.id())
        # check if we are editing a double_view panel
        if double_view is None:
            assert hints_file is not None
            self.hints_file = hints_file
            self.hints = hints_file.hints
            self.set_layout()
            global _edit_all
            if _edit_all:
                self.print_hints(self.hints, self.view)
                _edit_all = False
            else:
                self.print_hints(self.get_hints_in_regions(self.view.sel()), self.view)
        else:
            self.hints_file = double_view.hints_file
            self.hints = self.hints_file.hints
            hint_set = set()
            for region in self.view.sel():
                hint_set.update(double_view.hints_in_region(region))
            self.print_hints(hint_set, double_view.text_view)

    def get_hints_in_regions(self, regions):
        hint_set = set()
        for region in regions:
            for hint in self.hints:
                if hint not in hint_set:
                    for hint_region in hint.places:
                        if hint_region.intersects(region):
                            hint_set.add(hint)
                            break
        return hint_set

    def set_layout(self):
        self.view.window().run_command('set_layout',
                                       { "cols":  [0.0, 0.6, 1.0],
                                         "rows":  [0.0, 1.0],
                                         "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
                                       })

    def create_hint_view(self, view):
        result = view.window().new_file()
        result.window().run_command('move_to_group', {"group": 1})
        return result

    def print_hints(self, hints, text_view):
        def print_hint(view, hint):
            edit = view.begin_edit()
            try:
                view.insert(edit, view.size(), hint.text)
            finally:
                view.end_edit(edit)

        hint_counter = 0
        for hint in hints:
            hint_view = self.create_hint_view(text_view)
            hint_counter += 1
            hint_view.set_name("Hint " + str(hint_counter))
            print_hint(hint_view, hint)
            _displayed_hints[hint_view.id()] = { "file": self.hints_file,
                                                 "hint": hint,
                                                 "parent_view": text_view,
                                               }


class StopEditHintsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        id = self.view.id()
        if id in _displayed_hints:
            hints_file = _displayed_hints[id]["file"]
            hint = _displayed_hints[id]["hint"]
            parent_view = _displayed_hints[id]["parent_view"]

            hint.text = self.view.substr(sublime.Region(0, self.view.size()))
            hints_file.dump_json(parent_view)
            self.view.set_scratch(True)
            self.view.window().run_command("close_file")

            double_view = DoubleViewHintsCommand.find_by_target_view_id(parent_view.id())
            if double_view is not None:
                double_view.reload_hint_file()

            del _displayed_hints[id]


class CreateNewHintsFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.hints_file_name = self.view.file_name() + ".hints"
        if os.path.exists(self.hints_file_name):
            sublime.status_message("Error: file %s already exists" % self.hints_file_name)
            return
        self.view.window().show_input_panel("Author:", "", self.on_done, None, None)

    def on_done(self, user_input):
        source_file_name = self.view.file_name()
        now = datetime.now()
        meta = Meta(created = now,
                    modified = now,
                    author = user_input,
                    createdWith = "SublimeHints editor v0.1",
                    createdTimestamp = datetime.fromtimestamp(os.path.getctime(source_file_name)),
                    modifiedTimestamp = datetime.fromtimestamp(os.path.getmtime(source_file_name)),
                    md5sum = hashlib.md5(open(source_file_name, 'rb').read()).hexdigest())
        hint_file = HintFile(meta, [], self.hints_file_name)
        hint_file.dump_json(self.view)


class AppendHintCommand(HintsRenderer):

    def render(self, hints_file, **kwargs):
        self.hints_file = hints_file
        hint = Hint("")
        for region in self.view.sel():
            hint.places.append(region)
        self.hints_file.hints.append(hint)
        self.hints_file.dump_json(self.view)
        self.view.run_command("begin_edit_hints")


class EditAllHintsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        global _edit_all
        _edit_all = True
        self.view.run_command("begin_edit_hints")
