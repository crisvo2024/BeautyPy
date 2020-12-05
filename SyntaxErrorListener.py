from antlr4.error.ErrorListener import ErrorListener
import sys


class SyntaxErrorListener(ErrorListener):
    def __init__(self, data):
        self.view = data[0]
        self.edit = data[1]

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if "missing INDENT" in msg:
            self.view.insert(self.edit, self.view.text_point(line-1, 0), '    ')
        else:
            print("line " + str(line) + ":" + str(column) + " " + msg, file=sys.stderr)
