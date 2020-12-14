import sublime
import sublime_plugin
import os
import sys
import re
if not ((os.path.dirname(__file__) + '/gen') in sys.path):
    sys.path.append((os.path.dirname(__file__) + '/gen'))
from antlr4 import InputStream, CommonTokenStream
from Python3Lexer import Python3Lexer
from Python3Parser import Python3Parser
from .MyVisitor import MyVisitor
from .SyntaxErrorListener import SyntaxErrorListener


class Pep8Command(sublime_plugin.TextCommand):
    def run(self, edit):
        self.replace_mixed_indentation(edit)
        self.replace_not_multiple(edit)
        self.trailing_whitespace(edit)
        self.comment_handling(edit)
        self.blank_line_warning(edit)
        self.symbol_deprecated(edit)
        self.has_key_deprecated(edit)
        self.raise_exception(edit)
        # self.multiple_statements_colon(edit)
        self.new_line_end(edit)
        input_stream = InputStream(
            self.view.substr(
                sublime.Region(0, self.view.size())
            ))  # sublime.Region(0,self.view.size()))+ '\n'sin  w292
        lexer = Python3Lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = Python3Parser(stream)
        syntaxErrorListener = SyntaxErrorListener([self.view, edit])
        parser.removeErrorListeners()
        parser.addErrorListener(syntaxErrorListener)
        tree = parser.file_input()
        visitor = MyVisitor([self.view, edit])
        visitor.visit(tree)
        # self.multiple_statements_semicolon(edit)
        # self.eliminate_semicolons(edit)
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

    def trailing_whitespace(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            lines[index] = line.rstrip()
        self.view.replace(edit, allcontent, '\n'.join(lines))

    def new_line_end(self, edit):
        if sublime.Region(self.view.size()-1, self.view.size()) != '\n':
            self.view.insert(edit, self.view.size(), '\n')

    #def white_line_in_blankspace(self, edit): ya lo hace rstrip()

    def blank_line_warning(self, edit):
        allcontent = sublime.Region(0,self.view.size())
        ac = 0
        region = sublime.Region(self.view.size()-(1+ac),self.view.size()-ac)
        while '\n' == self.view.substr(region):
            ac+=1
            region = sublime.Region(self.view.size()-(1+ac),self.view.size()-ac)
        if ac > 1:
            
            blankLines = sublime.Region(self.view.size()-ac,self.view.size())
            self.view.replace(edit,blankLines,'\n')

    def symbol_deprecated(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            symbols = re.findall("<>", line)
            if symbols:
                lines[index] = line.replace(
                    "<>",
                    '!=',
                    symbols[0].count("<>"))
        self.view.replace(edit, allcontent, '\n'.join(lines))

    def is_char(self, char):
        if (ord(char)>64 and ord(char)<91) or (ord(char)>96 and ord(char)<123):
            return True
        return False

    def find_end_has_key(self, string):
        i = -1
        ac = 0
        for j in string:
            if not self.is_char(j) and j != "'" and j != '"' and j != '(' and j != ')':
                i = ac
                #print(i)
                return i
            ac+=1
        return

    def find_space(self,string):
        i = 0
        ac = 0
        for j in string:
            if not self.is_char(j):
                i = ac
                return i
            else:
                ac +=1
        ac = 0
        return

    def is_empty_string(self, string):
        ac = 0
        # print(string)
        for j in string:
            if j == ' ' or j=='\n' or j=='':
                ac += 1
        if ac == len(string):
            return True
        return False

    def has_key_deprecated(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            hasKeys = re.findall("has_key", line)
            if hasKeys:
                hasKeyIndex = line.find('has_key')
                parDerIndex = line.find(')')
                indexWord = self.find_space(line[0:hasKeyIndex])
                hasKeyEndIndex = self.find_end_has_key(line[hasKeyIndex+8:len(line)-1])
                obj = line[indexWord+1:hasKeyIndex-1] # donde se encuentra el objeto
                content = line[hasKeyIndex+8:hasKeyIndex+8+hasKeyEndIndex-1] # objeto si se verifica si se encuentra
                rest = line[hasKeyIndex+8+hasKeyEndIndex:len(line)-1]
                lines[index] = line[0:indexWord] + ' '+ content+' ' + 'in' + ' ' + obj + rest
        self.view.replace(edit, allcontent, '\n'.join(lines))

    def raise_exception(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            errors = re.findall("ValueError", line)
            if errors:
                errorIndex = line.find("ValueError")
                stringError = line[errorIndex+11:len(line)] # string que debe tener la excepción
                lines[index] = line[0:errorIndex-1] + " ValueError(" + stringError + ")"
        self.view.replace(edit, allcontent, '\n'.join(lines))

    def multiple_statements_colon(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            colons = re.findall(":", line)
            if colons:
                indexColon = line.find(":")
                strColon = line[indexColon+1:len(line)]
                if not self.is_empty_string(strColon):
                    lines[index] = line.replace(
                        ":",
                        ':\n\t',
                        colons[0].count(":"))
        self.view.replace(edit, allcontent, '\n'.join(lines))

    def multiple_statements_semicolon(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            colons = re.findall(";", line)
            if colons:
                indexColon = line.find(";")
                strColon = line[indexColon+1:len(line)]
                if not self.is_empty_string(strColon):
                    lines[index] = line.replace(
                        "; ",
                        ';\n')
        self.view.replace(edit, allcontent, '\n'.join(lines))

    def eliminate_semicolons(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            symbols = re.findall(";", line)
            if symbols:
                lines[index] = line.replace(
                    ";",
                    '',
                    symbols[0].count(";"))
        self.view.replace(edit, allcontent, '\n'.join(lines))

    # E261, E262, E265 and E266 (Arreglar indentaciones al principio):
    def comment_handling(self,edit):
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            # print(line)
            if '#' in line:
                # line = re.sub(r'\s*#[\s*#\s*]*',r'# ',line)
                # if not(line[0] == '#'):
                #     line = re.sub(r'#',r'  #',line)
                # lines[index] = line
                match = re.search(r'^\s*#[\s*#\s*]*',line)
                if not match:
                    line = re.sub(r'\s*#[\s*#\s*]*',r'  # ',line)
                else:
                    line = re.sub(r'#[\s*#\s*]*',r'# ',line)
                lines[index] = line
        self.view.replace(edit, allcontent, '\n'.join(lines))

