from antlr4.error.ErrorListener import ErrorListener
import sys
import re
import sublime


class SyntaxErrorListener(ErrorListener):
    def __init__(self, data):
        self.view = data[0]
        self.edit = data[1]
        self.errors = False

    #  E112 E113 E115 E116 E122
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        #  si faltan indentaciones añadirlas
        self.errors = True
        if "missing INDENT" in msg:
            self.view.insert(self.edit, self.view.text_point(line-1, 0), '    ')
        # si sobran indentaciones quitarlas
        elif "extraneous input '     " in msg:
            anterior = self.view.substr(self.view.line(self.view.text_point(line-2, 0)))
            indentations = re.findall(r'^\s*', anterior)
            actual = self.view.substr(self.view.line(self.view.text_point(line-1, 0)))
            actual = re.sub(r'^\s*', indentations[0], actual)
            self.view.replace(self.edit, self.view.line(self.view.text_point(line-1, 0)), actual)
            # self.view.erase(self.edit, sublime.Region(self.view.text_point(line-1, 0), self.view.text_point(line-1, 4)))
        # imprimir el error si es de otro tipo
        else:
            print("line " + str(line) + ":" + str(column) + " " + msg, file=sys.stderr)
