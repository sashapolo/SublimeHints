'''
@author: Oktay Acikalin <ok@ryotic.de>
Initially created: https://bitbucket.org/theblacklion/sublime_plugins/commits/3ea0c9e35d2f/
@author: Sam Kolton
Adapted for plugin SublimeHints

@license: MIT (http://www.opensource.org/licenses/mit-license.php)
'''

import sublime
import sublime_plugin

class Synchronizer(object):

    def __init__(self):
        self.timeout_min = 10
        self.timeout_max = 1000
        self.timeout = self.timeout_max
        self.timeout_inc_step = 10
        self.views = []

    def add_view(self, add_view):
        for view in self.views:
            if view.id() == add_view.id():
                return
        self.views.append(add_view)
        self.timeout = self.timeout_min

    def remove_view(self, remove_view):
        id = remove_view.id()
        for view in self.views:
            if view.id() == id:
                self.views.remove(view)
                return
    
    def clear_views(self):
        self.views = []  

    def prune_views(self):
        for view in self.views[:]:
            if not view.window():
                self.views.remove(view)
        if len(self.views) == 0:
            self.timeout = self.timeout_max

    def get_active_view(self):
        for view in self.views:
            window = view.window()
            if window:
                if window.active_view().id() == view.id():
                    return view
        return None

    def get_other_views(self):
        active_view = self.get_active_view()
        other_views = []
        for view in self.views:
            if view.id() == active_view.id():
                continue
            other_views.append(view)
        return other_views

    def run(self):
        # print '---', self.id, len(views), self.timeout
        self.prune_views()
        active_view = self.get_active_view()
        if active_view:
            settings = active_view.settings()
            last_row = settings.get('glue_views_last_row', None)
            cur_row, _ = active_view.rowcol(active_view.visible_region().begin())
            if last_row is not None:
                if last_row != cur_row:
                    self.timeout = self.timeout_min
                    diff = cur_row - last_row
                    # print 'active view', active_view.id(), 'diff', diff
                    for view in self.get_other_views():
                        row, _ = view.rowcol(view.visible_region().begin())
                        # print 'view', view.id(), 'currently at row', row
                        view.run_command('scroll_lines', dict(amount=-diff))
                        sels = view.sel()
                        if sels:
                            row, col = view.rowcol(sels[0].end())
                            sels.clear()
                            row += diff
                            sels.add(sublime.Region(view.text_point(int(row), col)))
                        view.settings().set('glue_views_last_row', None)
            settings.set('glue_views_last_row', cur_row)
        sublime.set_timeout(self.run, self.timeout)
        self.timeout += self.timeout_inc_step
        self.timeout = min(self.timeout, self.timeout_max)


class GlueViewsListener(sublime_plugin.EventListener):

    def on_activated(self, view):
        view.settings().set('glue_views_last_row', None)