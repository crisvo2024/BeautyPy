import sublime
import sublime_plugin
import os
import sys
import re
if not ((os.path.dirname(__file__)+'/gen') in sys.path):
    sys.path.append((os.path.dirname(__file__)+'/gen'))
from antlr4 import InputStream, CommonTokenStream
from Python3Lexer import Python3Lexer
from Python3Parser import Python3Parser
from .MyVisitor import MyVisitor
from .SyntaxErrorListener import SyntaxErrorListener


class Pep8Command(sublime_plugin.TextCommand):
    def run(self, edit):
        self.replace_mixed_indentation(edit)
        self.replace_not_multiple(edit)
        input_stream = InputStream(
            self.view.substr(
                sublime.Region(0, self.view.size())
            ) + '\n')
        lexer = Python3Lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = Python3Parser(stream)
        syntaxErrorListener = SyntaxErrorListener([self.view, edit])
        parser.removeErrorListeners()
        parser.addErrorListener(syntaxErrorListener)
        tree = parser.file_input()
        visitor = MyVisitor([self.view, edit])
        visitor.visit(tree)
        # self.view.insert(edit, 110, "Hello, World!")

    def replace_mixed_indentation(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            indentations = re.findall(r"^(\s*\t+)+", line)
            if indentations:
                lines[index] = line.replace(
                    '\t', 
                    '    ',
                    indentations[0].count('\t'))
        self.view.replace(edit, allcontent, '\n'.join(lines))

    def replace_not_multiple(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            indentations = re.findall(r"^\s+", line)
            if indentations:
                if len(indentations[0]) % 4 != 0:
                    lines[index] = ''.join([
                        ' ' for _ in range(4-(len(indentations[0]) % 4))
                    ]) + line
        self.view.replace(edit, allcontent, '\n'.join(lines))
