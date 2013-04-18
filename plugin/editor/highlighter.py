'''
Created on Apr 1, 2013

@author: snowball
'''

import sublime


class HintsHighlighter(object):
    def __init__(self, view, hints = None):
        self.view = view
        self.hints = hints

    def highlight_hints(self, key, style):
        assert (self.hints is not None)

        def highlight_regions(name):
            self.view.add_regions(name,
                                  self.regions[name],
                                  style,
                                  "bookmark",
                                  sublime.DRAW_OUTLINED | sublime.DRAW_EMPTY_AS_OVERWRITE)

        self.regions = {key: []}
        for hint in self.hints:
            for region in hint.places:
                self.regions[key].append(region)
        highlight_regions(key)

    def unhighlight_hints(self, key):
        self.view.erase_regions(key)
