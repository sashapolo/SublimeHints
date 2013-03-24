'''
Created on Mar 17, 2013

@author: snowball
'''

from SublimeHints import HintsRenderer
import sublime_plugin
import sublime


class HighlightHintsCommand(HintsRenderer):
    _regions_key = "highlighter"
    _highlighted_views = {}

    def render(self, hints_file):
        highlighted = self._highlighted_views.setdefault(self.view.id, False)

        if not highlighted:
            self.highlight_hints(self.view, hints_file.hints, self._regions_key, "comment")
            self._highlighted_views[self.view.id] = True
        else:
            self.view.erase_regions(self._regions_key)
            self._highlighted_views[self.view.id] = False

    @staticmethod
    def highlight_hints(view, hints, name, style):
        regions = {name: []}
        for hint in hints:
            for region in hint.places:
                regions[name].append(region)
        HighlightHintsCommand.highlight_regions(view, regions, name, style)

    @staticmethod
    def highlight_regions(view, regions, name, style):
        view.add_regions(name,
                         regions[name],
                         style,
                         "bookmark",
                         sublime.DRAW_OUTLINED | sublime.DRAW_EMPTY_AS_OVERWRITE)


class DisplaySelectedHintsCommand(HintsRenderer):
    _regions_key = "selecter"

    @classmethod
    def get_regions_key(self):
        return self._regions_key

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

        HighlightHintsCommand.highlight_hints(self.view,
                                              displayed_hints,
                                              self._regions_key,
                                              "string")

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
        return "(line " + str(row + 1) + ", col " + str(col + 1) + ")"


class ClearEditSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase_regions(DisplaySelectedHintsCommand.get_regions_key())
        panel = self.view.window().get_output_panel("hints")
        self.view.window().run_command("hide_panel")
