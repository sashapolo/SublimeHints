'''
Created on Mar 17, 2013

@author: alexander
'''

from SublimeHints import HintsRenderer
import os
import sys
try:
    import sublime
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'util'))
    import sublime


class OutputPanelHintsCommand(HintsRenderer):
    def render(self, hints_file):
        self.print_hints(hints_file.hints)
        self.highlight_hints(hints_file.hints)

    def format_hints(self, hints):
        result = self.view.file_name() + ":\n"
        i = 1
        for hint in hints:
            result += "=" * 8 + " Hint " + str(i) + " " + "=" * 8 + "\n"
            result += self.format_hint(hint)
            i += 1
        return result

    def format_hint(self, hint):
        result = ""
        for region in hint.places:
            (row, col) = self.view.rowcol(region.begin())
            result += "((" + str(row) + ":" + str(col) + ") - "
            (row, col) = self.view.rowcol(region.end())
            result += "(" + str(row) + ":" + str(col) + ")) "
        return result + "\n\n" + hint.text + "\n\n"

    def highlight_hints(self, hints):
        regions = {"hints": []}
        for hint in hints:
            for region in hint.places:
                regions["hints"].append(region)
        self.highlight_regions(regions)

    def highlight_regions(self, regions):
        self.view.add_regions("hints",
                              regions["hints"],
                              "string",
                              "bookmark",
                              sublime.DRAW_OUTLINED)

    def print_hints(self, hints):
        panel = self.view.window().get_output_panel("hints")
        panel.set_read_only(False)
        edit = panel.begin_edit()
        try:
            panel.erase(edit, sublime.Region(0, panel.size()))
            panel.insert(edit, panel.size(), self.format_hints(hints))
        finally:
            panel.set_read_only(True)
            panel.end_edit(edit)
        self.view.window().run_command("show_panel", {"panel": "output.hints"})
