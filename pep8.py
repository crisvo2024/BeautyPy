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

class Pep8Command(sublime_plugin.TextCommand):
    def run(self, edit):
        self.replace_mixed_indentation(edit)
        self.replace_not_multiple(edit)
        self.trailing_whitespace(edit)
        self.new_line_end(edit)
        self.blank_line_warning(edit)
        input_stream = InputStream(self.view.substr(sublime.Region(0,self.view.size()))) # sublime.Region(0,self.view.size()))+'\n' sin  w292
        lexer = Python3Lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = Python3Parser(stream)
        tree = parser.file_input()
        visitor = MyVisitor([self.view,edit])
        visitor.visit(tree)
        # self.view.insert(edit, 110, "Hello, World!")

    def replace_mixed_indentation(self,edit):
        allcontent = sublime.Region(0,self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            indentations = re.findall("^(\s*\t+)+", line)
            if indentations:
                lines[index] = line.replace('\t','    ',indentations[0].count('\t'))
        self.view.replace(edit,allcontent,'\n'.join(lines))

    def replace_not_multiple(self,edit):
        allcontent = sublime.Region(0,self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            indentations = re.findall("^\s+", line)
            if indentations:
                if len(indentations[0]) % 4 != 0:
                    lines[index] = ''.join([' ' for _ in range(4-(len(indentations[0]) % 4))]) + line
        self.view.replace(edit,allcontent,'\n'.join(lines))

    def trailing_whitespace(self, edit):
        allcontent = sublime.Region(0,self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index,line in enumerate(lines):
            lines[index] = line.rstrip();
        self.view.replace(edit,allcontent,'\n'.join(lines)) 

    def new_line_end(self, edit):
        if sublime.Region(self.view.size()-1,self.view.size()) != '\n':
            self.view.insert(edit, self.view.size(), '\n')

    # def white_line_in_blankspace(self, edit): ya lo hace rstrip()
    
    # def blank_line_warning(self, edit):
    #     allcontent = sublime.Region(0,self.view.size())
    #     ac = 0
    #     region = sublime.Region(self.view.size()-(1+ac),self.view.size()-ac)
    #     while '\n' in self.view.substr(region):
    #         ac+=1
    #         region = sublime.Region(self.view.size()-(1+ac),self.view.size()-ac)
    #     if ac > 1:
    #         blankLines = sublime.Region(self.view.size()-ac,self.view.size())
    #         lines = self.view.substr(blankLines).splitlines()
    #         for index, line in enumerate(lines):
    #             lines[index] = ''
    #         self.view.replace(edit,blankLines,'\n'.join(lines))

