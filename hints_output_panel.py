'''
Created on Mar 17, 2013

@author: alexander
'''

from hints import HintsFileNotFoundError, HintFormatError, HintFile
import logging
import os
import sublime
import sublime_plugin


class ShowHintsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            hints_file = self.load_hints_file()
        except (HintsFileNotFoundError, HintFormatError) as ex:
            logging.exception(ex)
            return
        self.print_hints(hints_file.hints)

    def load_hints_file(self):
        hints_file = self.view.file_name() + ".hints"
        if not os.path.exists(hints_file):
            raise HintsFileNotFoundError("Hint file %s not found", hints_file)

        hints_file = HintFile.load_json(self.view, hints_file)
        return hints_file

    def format_hint(self, hint, i):
        return self.view.file_name() + ": hint " + str(i) + "\n" + hint.text + "\n"

    def print_hints(self, hints):
        panel = self.view.window().get_output_panel("hints")
        panel.set_read_only(False)
        edit = panel.begin_edit()
        panel.erase(edit, sublime.Region(0, panel.size()))
        i = 1
        for hint in hints:
            panel.insert(edit, panel.size(), self.format_hint(hint, i))
            i += 1
        panel.set_read_only(True)
        self.view.window().run_command("show_panel", {"panel": "output.hints"})
        panel.end_edit(edit)
