 # -*- coding: UTF-8-*-

from hints import *
import logging
import os
import string

logging.basicConfig(level=logging.DEBUG)

# if plugins was launched with internal Sublime python interpreter
# sublime module will be available, otherwise use stub

try:
    import sublime
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'util'))
    import sublime

# don't forget about correct .pth file in your path pointing to Sublime installation
import sublime_plugin

class AllHintsFoldedCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            hints_file = self.load_hints_file()
        except (HintsFileNotFoundError, HintFormatError) as ex:
            logging.exception(ex)	
            return

        self.fhf = self.view.window().new_file() # fhf = fold_hint_file
        self.fhf.set_scratch(True)
        self.fhf_edit = self.fhf.begin_edit()
        try:
            self.copy_file()
            self.insert_hints(hints_file.hints)
        finally:
            self.fhf.end_edit(self.fhf_edit)



    def load_hints_file(self):
        hints_file = self.view.file_name() + ".hints"
        if not os.path.exists(hints_file):
            raise HintsFileNotFoundError("Hint file %s not found", hints_file)
        
        hints_file = HintFile.load_json(self.view, hints_file)
        return hints_file


    def copy_file(self):
        full_region = sublime.Region(0, self.view.size())
        contents = self.view.substr(full_region)
        self.fhf.insert(self.fhf_edit, 0, contents)


    def format_hint(self, hint):
        u"""
        Форматирование текста хинта для вставки во временный файл. Текущий формат:
           ==========Hint==========
           Текст хинта
           ========================
        Вначале каждой строки вставлено по 3 пробела для формирования блока сворачивания текста
        """
        header = "=" * 10  + "Hint" + "=" * 10 + "\n"
        equals = "\n" + "=" * 24  + "\n"
        text = header + hint.text + equals
        lines = map(lambda s: 3 * " " + s.lstrip(), text.splitlines())
        text = "\n" + string.join(lines, "\n")
        # Проверка необходимости завершающего перевода строки. 
        # Он необходим если текст, к которому относится хинт заканчивается не в конце строки
        end_line = self.view.line(hint.places[0].end())
        _, end_col = self.view.rowcol(end_line.end())
        _, col = self.view.rowcol(hint.places[0].end())
        if col < end_col:
            return text + "\n"
        else:
            return text

    def insert_hints(self, hints):
        # формирование списка хинтов, где каждый хинт отнесен к ровно одной области
        single_hints = list()
        for hint in hints:
            for place in hint.places:
                single_hints.append(Hint(hint.text, [place]))
        # сортировка этого списка по убыванию старшей границы диапазона хинта
        single_hints.sort(None, key=lambda h: h.places[0].end(), reverse=True)
        
        self.fhf.add_regions("basic_text", map(lambda hint: hint.places[0], single_hints), "comment", "dot", sublime.DRAW_OUTLINED)
        for hint in single_hints:
            self.insert_hint(hint)
       
    def insert_hint(self, hint):
        for place in hint.places:
            text = self.format_hint(hint)
            self.fhf.insert(self.fhf_edit, place.end(), text)
            self.fhf.fold(sublime.Region(place.end(), place.end()+len(text)))
            
