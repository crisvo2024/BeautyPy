from antlr4.error.ErrorListener import ErrorListener
import sys
import sublime


class SyntaxErrorListener(ErrorListener):
    def __init__(self, data):
        self.view = data[0]
        self.edit = data[1]

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        #  si faltan indentaciones añadirlas
        if "missing INDENT" in msg:
            self.view.insert(self.edit, self.view.text_point(line-1, 0), '    ')
        # si sobran indentaciones quitarlas
        elif "extraneous input '     " in msg:
            self.view.erase(self.edit, sublime.Region(self.view.text_point(line-1, 0), self.view.text_point(line-1, 4)))
        # imprimir el error si es de otro tipo
        else:
            print("line " + str(line) + ":" + str(column) + " " + msg, file=sys.stderr)
