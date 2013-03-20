# -*- coding: utf-8 -*-

import os
import sys
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


class ForceReloadCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # in sublime internal environment the following doesn't work
        # path = os.path.realpath(__file__)
        path = os.path.join(sublime.packages_path(), __name__, __file__)
        logging.debug('Reloading file: %s' % path)
        sublime_plugin.reload_plugin(path)


class HintsRenderer(sublime_plugin.TextCommand):
    def run(self, edit):
        self.edit = edit
        self.window = sublime.active_window()
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
            self.render(hints_file)

    def render(self, hints_file):
        raise NotImplementedError('HintsRenderer command should not be called directly')


class DumbRendererCommand(HintsRenderer):
    def render(self, hints_file):
        def on_load(selected):
            logging.debug('Hint: %s selected', hints_file.hints[selected])
        self.window.show_quick_panel([hint.text for hint in hints_file.hints], on_load)


class AllHintsFoldedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        import hintsfold
        hintsfold.AllHintsFoldedCommand.run(self, edit)
