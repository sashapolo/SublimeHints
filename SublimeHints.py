 # -*- coding: cp1251 -*-
import os, sys
from hints import *
import logging


logging.basicConfig(level=logging.DEBUG)

# if plugins was launched with internal Sublime python interpreter
# sublime module will be available, otherwise use stub

try:
    import sublime
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'util'))
    import sublime

# don't forget about correct .pth file in your path pointing to Sublime installation
import sublime_plugin

class FetchAndLoadHints(sublime_plugin.EventListener):
    pass

class FindHintsCommand(sublime_plugin.TextCommand):
    """Try to find file with hints and show them in separate window."""

    def run(self, edit):
        full_path = self.view.file_name()
        hints_file = full_path + ".hints"
        if not os.path.exists(hints_file):
            logging.info("Hint file %s not found", hints_file)
            return
        try:
            hints_file = HintFile.load_json(self.view, hints_file)
        except HintFormatError:
            logging.exception("Can't load hint file %s", hints_file)
        else:
            active_window = sublime.active_window()
            def on_load(selected):
                logging.debug('Hint: %s selected', hints_file.hints[selected])
            active_window.show_quick_panel([hint.text for hint in hints_file.hints], on_load)


class AllHintsFoldedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        import hintsfold
        hintsfold.AllHintsFoldedCommand.run(self, edit)