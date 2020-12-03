import sublime
import sublime_plugin 
from .gen.antlr4 import *
from .gen.Python3Lexer import Python3Lexer
from .gen.Python3Parser import Python3Parser
from MyVisitor import MyVisitor 


class Pep8Command(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.insert(edit, 110, "Hello, World!")
		input_stream = InputStream(sublime.Region(0, self.view.size()))
		lexer = Python3Lexer(input_stream)
		stream = CommonTokenStream(lexer)
		parser = Python3Parser(stream)
		tree = parser.file_input()
		visitor = MyVisitor()
		visitor.visit(tree) 
		self.view.insert(edit, 110, "Hello, World!")
 