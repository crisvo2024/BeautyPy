import sublime
import sublime_plugin 
import os
import sys
if not ((os.path.dirname(__file__)+'/gen') in sys.path):
    sys.path.append((os.path.dirname(__file__)+'/gen'))
from antlr4 import *
from Python3Lexer import Python3Lexer
from Python3Parser import Python3Parser
from .MyVisitor import MyVisitor

class Pep8Command(sublime_plugin.TextCommand):
    def run(self, edit):
        input_stream = FileStream(self.view.file_name(), 'utf-8')
        lexer = Python3Lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = Python3Parser(stream)
        tree = parser.file_input()
        visitor = MyVisitor([self.view,edit])
        visitor.visit(tree) 
        # self.view.insert(edit, 110, "Hello, World!")