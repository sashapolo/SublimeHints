# -*- coding: utf-8 -*-

import os
import sys
from hints import *
import logging
import tempfile

import sublime
import sublime_plugin

# insert plugin directory in path
PLUGIN_DIRECTORY = os.path.join(sublime.packages_path(), __name__)
if PLUGIN_DIRECTORY not in sys.path:
    sys.path.insert(0, PLUGIN_DIRECTORY)

logging.basicConfig(level=logging.DEBUG)


class SublimeUtilMixin(object):
    """Auxiliary mixin class that adds various helper methods
     to indeed rather clumsy Sublime Text API
     """

    def __init__(self, *args, **kwargs):
        super(SublimeUtilMixin, self).__init__(*args, **kwargs)
        self.window = self.view.window()
        self.settings = self.view.settings()

    def file_region(self):
        """Returns sublime.Region instance including whole content of
        buffer
        """
        return sublime.Region(0, self.view.size())

    def file_content(self):
        """Returns whole file content as string"""
        return self.view.substr(self.file_region())

    def line_region(self, lineno):
        """Returns specified line as sublime.Region.
        If line index is out of range the values is (lastchar, lastchar)
        Line numbers start from zero.
        """
        return self.view.line(self.view.text_point(lineno, 0))

    def line_content(self, lineno):
        """Returns content of specified line or empty string if line number
        is out of range.
        Line numbers start from zero.
        """
        return self.view.substr(self.line_region(lineno))

    def lines_regions(self, start=0, end=None):
        """Returns lines of buffer as list of elements of type sublime
        .Region"""
        return self.view.lines(self.file_region())[start:end]

    def lines_content(self, start=0, end=None):
        """Returns lines of buffer as list of strings"""
        return map(self.view.substr, self.lines_regions(start, end))

    def _initialize_buffer(self, view, content=None, name=None, readonly=False, scratch=False):
        logging.debug('In _initialize_buffer')
        if content:
            edit = view.begin_edit()
            try:
                logging.debug('Editing tempfile')
                view.insert(edit, 0, content)
            finally:
                view.end_edit(edit)
        if name:
            view.set_name(name)
        view.set_read_only(readonly)
        view.set_scratch(scratch)

    def new_file(self, content=None, name=None, readonly=False, scratch=False):
        """Opens new empty tab and optionally sets its name and fill buffer
        with content.
        Scratch option means that Sublime will not show such file as modified
        (dirty) and will not ask you to save it on close.
        """
        new_view = self.window.new_file()
        self._initialize_buffer(new_view, content, name, readonly, scratch)
        return new_view

    def temp_file(self, suffix='', prefix='', content=None, name=None,
                  readonly=False,
                  scratch=False):
        """Creates new temporary file. Prefix and suffix is added to randomly
        generated name. All other options are the same as in new_file method.
        """
        import time
        _, filename = tempfile.mkstemp(suffix, prefix)
        new_view = self.window.open_file(filename)
        for i in range(10):
            if not new_view.is_loading():
                break
            print '=',
            time.sleep(1)
        self._initialize_buffer(new_view, 'Eggs', name, readonly, scratch)
        return new_view


class TestCommand(SublimeUtilMixin, sublime_plugin.TextCommand):
    folded = False

    def run(self, edit):
        # regions = self.lines_regions(0, 5)
        # area = regions[0].cover(regions[-1])
        # if TestCommand.folded:
        #     self.view.unfold(area)
        # else:
        #     self.view.fold(area)
        # TestCommand.folded = not TestCommand.folded
        # self.new_file(self.file_content(), name='Eggs', readonly=True, scratch=True)
        # logging.debug(self.file_content())
        f = self.temp_file(prefix='tmp', content=self.file_content(), name='foo')
        e = f.begin_edit()
        f.insert(e, 0, 'spam!')
        f.end_edit(e)
        self.window.focus_view(self.view)


class ForceReloadCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # in sublime internal environment the following doesn't work
        # path = os.path.realpath(__file__)
        path = os.path.join(sublime.packages_path(), __name__, __file__)
        logging.debug('Reloading file: %s' % path)
        sublime_plugin.reload_plugin(path)


class HintsRenderer(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(HintsRenderer, self).__init__(*args, **kwargs)

    def run(self, edit):
        self.edit = edit
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
        raise NotImplementedError(
            'HintsRenderer should not be called directly')


class DumbRendererCommand(HintsRenderer):
    def render(self, hints_file):
        def on_load(selected):
            logging.debug('Hint: %s selected', hints_file.hints[selected])

        self.window.show_quick_panel([hint.text for hint in hints_file.hints],
                                     on_load)


class ShowPathCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        import pprint

        pprint.pprint(sys.path)
