# -*- coding: utf-8 -*-

import os
import sys
from hints import *
import logging
import tempfile

import sublime
import sublime_plugin

# insert plugin and third-party libraries directories in path
# NOTE: it can't be determined as os.path.dirname(__file__) in sublime interpreter
PLUGIN_DIRECTORY = os.path.join(sublime.packages_path(), __name__)
LIB_DIRECTORY = os.path.join(PLUGIN_DIRECTORY, 'lib')
if PLUGIN_DIRECTORY not in sys.path:
    sys.path.insert(0, PLUGIN_DIRECTORY)
    sys.path.insert(0, LIB_DIRECTORY)

# Logging setup

# plugin root logger
logger = logging.getLogger('SublimeHints')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('[%(levelname)s]:%(name)s: %(message)s'))
logger.addHandler(console_handler)
logger.propagate = False


class SublimeUtilMixin(object):
    """Auxiliary mixin class that adds various helper methods
     to indeed rather clumsy Sublime Text API
     """
    logger = logging.getLogger('SublimeHints.SublimeUtilMixin')
    logger.setLevel(logging.DEBUG)

    def __init__(self, *args, **kwargs):
        super(SublimeUtilMixin, self).__init__(*args, **kwargs)
        self.window = sublime.active_window()
        self.settings = self.view.settings()

    def file_type(self):
        """Returns file type associated with start of the first selection"""
        first_cursor = self.view.sel()[0].begin()
        return self.view.scope_name(first_cursor).split('.')[-1].strip()

    def file_name(self):
        """Returns final part of buffer name or None if it isn't saved yet"""
        name = self.view.file_name()
        return os.path.basename(name) if name is not None else None

    def file_path(self):
        """Returns absolute path to file or None if it isn't saved yet"""
        return self.view.file_name()

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
        SublimeUtilMixin.logger.debug('_initialize_buffer() called')
        if content:
            if view.is_loading:
                SublimeUtilMixin.logger.error("file %s can't be edited", view.file_name())
                return
            edit = view.begin_edit()
            try:
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

    def temp_file(self, suffix='', prefix='', content=None, name=None, readonly=False, scratch=False, focus=False):
        """Creates new temporary file. Prefix and suffix is added to randomly
        generated name. All other options are the same as in new_file method.
        """
        _, filename = tempfile.mkstemp(suffix, prefix)
        with open(filename, 'w') as tmp:
            tmp.write(content)
        new_view = self.window.open_file(filename)
        self._initialize_buffer(new_view, None, name, readonly, scratch)
        # change focus to current view again
        if not focus:
            self.window.focus_view(self.view)
        return new_view


class TestCommand(SublimeUtilMixin, sublime_plugin.TextCommand):
    folded = False

    def __init__(self, view):
        logger.debug('TestCommand initialized')
        super(TestCommand, self).__init__(view)

    def run(self, edit):
        # regions = self.lines_regions(0, 5)
        # area = regions[0].cover(regions[-1])
        # if TestCommand.folded:
        #     self.view.unfold(area)
        # else:
        #     self.view.fold(area)
        # TestCommand.folded = not TestCommand.folded

        # content = '\n'.join(self.lines_content(end=10))
        # self.temp_file(suffix='.xhtml', content=content, name='foo', focus=False)

        logger.info('File type: %s', self.file_type())

class HintsRenderer(SublimeUtilMixin, sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(HintsRenderer, self).__init__(*args, **kwargs)

    def run(self, edit):
        self.edit = edit
        full_path = self.view.file_name()
        hints_file = full_path + ".hints"
        if not os.path.exists(hints_file):
            logger.info("Hint file %s not found", hints_file)
            return
        try:
            hints_file = HintFile.load_json(self.view, hints_file)
        except HintFormatError:
            logger.exception("Can't load hint file %s", hints_file)
        else:
            logger.debug('HintsRenderer.render() is called')
            self.render(hints_file)

    def render(self, hints_file):
        raise NotImplementedError('HintsRenderer.render() should not be called directly')

# Miscellaneous commands section
try:
    from test import TestPluginCommand
except ImportError:
    logger.exception("Possibly missing dependency in 'test'")
try:
    from viewers.browser import BrowserViewCommand
except ImportError as e:
    logger.exception("Possibly missing dependency in 'viewers.browser'")

from double_view import *
from hint_editor import *