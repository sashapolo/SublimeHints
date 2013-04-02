import nose

import sublime_plugin

class TestPluginCommand(sublime_plugin.TextCommand):
    """This command runs all tests of the plugin.
    This allows to run tests within Python runtime that is embedded into Sublime.
    If tests are run within an external Python runtime it's not possible to import sublime module.
    """
    def run(self, edit):
        from test import testhints
        testhints._current_view = self.view
        nose.run(argv=['--where', PLUGIN_DIRECTORY + "/test"])