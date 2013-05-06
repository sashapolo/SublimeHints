'''
@author: Oktay Acikalin <ok@ryotic.de>
Initially created: https://bitbucket.org/theblacklion/sublime_plugins/commits/3ea0c9e35d2f/
@author: Sam Kolton
Adapted for plugin SublimeHints

@license: MIT (http://www.opensource.org/licenses/mit-license.php)
'''

import sublime

class Synchronizer(object):

    def __init__(self, view1 = None, view2 = None):
        self.timeout = 10
        self.views = []
        self.views.append(view1)
        self.views.append(view2)
        self.last_viewport = (-1.0, -1.0)

    def add_view(self, add_view):
        for view in self.views:
            if view.id() == add_view.id():
                return
        self.views.append(add_view)
        sublime.set_timeout(self.run, self.timeout)

    def remove_view(self, remove_view):
        id = remove_view.id()
        for view in self.views:
            if view.id() == id:
                self.views.remove(view)
                return
    
    def clear_views(self):
        self.views = []  

    
    def get_other_views(self, cur_view):
        other_views = []
        for view in self.views:
            if view.id() == cur_view.id():
                continue
            other_views.append(view)
        return other_views

    def run(self):
        if len(self.views) == 0:
            return
        for view in self.views:
            if view.viewport_position() != self.last_viewport:
                new_viewport = view.viewport_position()
                for other_view in self.get_other_views(view):
                    other_view.set_viewport_position(new_viewport, True)
                self.last_viewport = new_viewport
                break
        sublime.set_timeout(self.run, self.timeout)

