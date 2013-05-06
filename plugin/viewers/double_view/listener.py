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
        lines = []
        for region in selected:
            lines.extend(hint_view.lines(region))
        #print lines
        line_numbers = map(lambda x: (hint_view.rowcol(x.begin()))[0], lines)

        command.text_view.erase_regions("text_highlight")
        for line_number in line_numbers:
            hint = command.find_hint_repr(line_number)
            if hint != None:
                self.__highlight_hint(command, hint)


    def __highlight_hint(self, command, hint):
        text_view = command.text_view
        regions = text_view.get_regions("text_highlight")
        regions.append(hint.text_place)
        text_view.add_regions("text_highlight", regions, "comment", "bookmark")  