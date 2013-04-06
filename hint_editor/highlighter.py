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
        assert (self.hints != None)

        self.regions = {key: []}
        for hint in self.hints:
            for region in hint.places:
                self.regions[key].append(region)
        self.highlight_regions(key, style)

    def highlight_regions(self, name, style):
        self.view.add_regions(name,
                              self.regions[name],
                              style,
                              "bookmark",
                              sublime.DRAW_OUTLINED | sublime.DRAW_EMPTY_AS_OVERWRITE)

    def unhighlight_hints(self, key):
        self.view.erase_regions(key)
