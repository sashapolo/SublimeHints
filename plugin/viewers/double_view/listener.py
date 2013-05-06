import sublime, sublime_plugin
from double_view import DoubleViewHintsCommand

class SelectionListener(sublime_plugin.EventListener):
    
    def on_selection_modified(self, view):
        if not DoubleViewHintsCommand.activate_listener:
            return

        activated = DoubleViewHintsCommand.activated
        id = view.id()
        command = DoubleViewHintsCommand.find_by_hint_view_id(id)
        if command == None:
            return
        else:
            self.__highlight(command)


    def __highlight(self, command):
        hint_view = command.hint_view.view
        selected = hint_view.sel()
        command.text_view.erase_regions("text_highlight")
        hints = []
        for region in selected:
            hints.extend(command.hints_in_region_repr(region))
        for hint in hints:
            self.__highlight_hint(command, hint)


    def __highlight_hint(self, command, hint):
        text_view = command.text_view
        regions = text_view.get_regions("text_highlight")
        regions.append(hint.text_place)
        text_view.add_regions("text_highlight", regions, "comment", "bookmark")  