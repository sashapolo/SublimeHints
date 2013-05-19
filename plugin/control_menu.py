import sublime, sublime_plugin
import SublimeHints
from viewers.double_view import DoubleViewHintsCommand


class HintsMenuCommand(SublimeHints.HintsRenderer):
    
    def render(self, hints_file, **kwargs):
        self.hints_file = hints_file
        print hints_file
        commands = {}
        if DoubleViewHintsCommand.find_by_target_view_id(self.view.id()):
            commands[0] = CloseDoubleView()
        else:
            commands[0] = ShowDoubleView()
        commands[1] = ShowBrowser()
        commands[2] = EditAllHints()
        
        self.view.window().show_quick_panel(commands.values(), lambda x: self.on_done(commands, x))
        
    def on_done(self, commands, index):
        if index == -1:
            return
        commands[index].on_done(self)




class MenuItem(str):
    def __new__(cls, string=""):
        ob = super(MenuItem, cls).__new__(cls, string)
        return ob

    def on_done(self, menu):
        raise NotImplementedError('MenuItem.on_done() should not be called directly')


class ShowDoubleView(MenuItem):
    def __new__(cls):
        return super(ShowDoubleView, cls).__new__(cls, "Show hints in double view.")

    def on_done(self, menu):
        hints = menu.hints_file.hints
        tags = set()
        for hint in hints:
            for tag in hint.tags:
                tags.add(tag)
        tags = list(tags)
        if not tags: 
            menu.view.run_command("double_view_hints")
        else:
            tags.insert(0, "All tags...")
            menu.view.window().show_quick_panel(tags, lambda x: self.tags_done(menu, tags, x))

    def tags_done(self, menu, tags, index):
        if index == -1:
            return
        elif index == 0:
            menu.view.run_command("double_view_hints")
        else:
            menu.view.run_command("double_view_hints", {"tags": [tags[index]]})


class CloseDoubleView(MenuItem):
    def __new__(cls):
        return super(CloseDoubleView, cls).__new__(cls, "Close double view.")

    def on_done(self, menu):
        menu.view.run_command("double_view_hints") 


class ShowBrowser(MenuItem):
    def __new__(cls):
        return super(ShowBrowser, cls).__new__(cls, "Show hints in browser.")

    def on_done(self, menu):
        menu.view.run_command("browser_view") 


class EditAllHints(MenuItem):
    def __new__(cls):
        return super(EditAllHints, cls).__new__(cls, "Edit all hints.")

    def on_done(self, menu):
        menu.view.run_command("edit_all_hints")   