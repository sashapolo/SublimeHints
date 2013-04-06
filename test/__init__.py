import sublime_plugin
import os.path

_current_view = None

class TestPluginCommand(sublime_plugin.TextCommand):
    """This command runs all tests of the plugin.
    This allows to run tests within Python runtime that is embedded into Sublime.
    If tests are run within an external Python runtime it's not possible to import 
    sublime module.
    """

    def run(self, edit):
        import nose
        import SublimeHints
        global _current_view
        _current_view = self.view
        nose.run(argv=['--where', os.path.join(SublimeHints.PLUGIN_DIRECTORY, 'test')])