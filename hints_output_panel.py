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


class HighlightHintsCommand(HintsRenderer):
    def render(self, hints_file):
        self.highlight_hints(hints_file.hints)

    def highlight_hints(self, hints):
        regions = {"hints": []}
        for hint in hints:
            for region in hint.places:
                regions["hints"].append(region)
        self.highlight_regions(regions)

    def highlight_regions(self, regions):
        self.view.add_regions("hints",
                              regions["hints"],
                              "comment",
                              "bookmark",
                              sublime.DRAW_OUTLINED)


class DisplaySelectedHintsCommand(HintsRenderer):
    def render(self, hints_file):
        panel = self.view.window().get_output_panel("hints")
        panel.set_read_only(False)
        edit = panel.begin_edit()
        try:
            panel.erase(edit, sublime.Region(0, panel.size()))
            self.print_hints(hints_file.hints, edit, panel)
        finally:
            panel.set_read_only(True)
            panel.end_edit(edit)
        self.view.window().run_command("show_panel", {"panel": "output.hints"})

    def print_hints(self, hints, edit, panel):
        panel.insert(edit, panel.size(), self.view.file_name() + ":\n")
        displayed_hints = set()
        # this piece of code is fucked up
        for region in self.view.sel():
            for hint in hints:
                if hint not in displayed_hints:
                    for hint_region in hint.places:
                        if hint_region.intersects(region):
                            self.print_hint(hint, edit, panel)
                            displayed_hints.add(hint)
                            break

    def print_hint(self, hint, edit, panel):
        panel.insert(edit, panel.size(), "=" * 8 + " Hint " + "=" * 8 + "\n")
        panel.insert(edit, panel.size(), self.format_hint(hint))

    def format_hint(self, hint):
        result = ""
        for region in hint.places:
            result += self.format_rowcol(*self.view.rowcol(region.begin())) + " -- "
            result += self.format_rowcol(*self.view.rowcol(region.end())) + "\n"
        return result + "\n" + hint.text + "\n\n"

    def format_rowcol(self, row, col):
        return "(line " + str(row + 1) + ", column " + str(col + 1) + ")"
