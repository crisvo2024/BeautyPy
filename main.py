# Cristian Santiago Vargas Ortiz
# Juan Esteban Rozo Urbina
# Juan Camilo Acosta Rojas
import sys
import os
from antlr4 import *
from gen.Python3Lexer import Python3Lexer
from gen.Python3Parser import Python3Parser
from AntiVisitor import AntiVisitor


def main(argv):
    directory = os.path.dirname(__file__)
    # file = open(directory+"/input.txt", "wt")
    # file.writelines(sys.stdin.readlines())
    # file.close()
    input_stream = FileStream(directory+"/pep8.py", 'utf-8')
    lexer = Python3Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Python3Parser(stream)
    tree = parser.file_input()
    visitor = AntiVisitor([0, 0])
    visitor.visit(tree)
    print('hola')


if __name__ == '__main__':
    main(sys.argv)
