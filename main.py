# Cristian Santiago Vargas Ortiz
# Juan Esteban Rozo Urbina
# Juan Camilo Acosta Rojas
import sys
import os
from antlr4 import FileStream, CommonTokenStream
from gen.Python3Lexer import Python3Lexer
from gen.Python3Parser import Python3Parser
from AntiVisitor import AntiVisitor
from SyntaxErrorListener import SyntaxErrorListener

def main(argv):
    directory = os.path.dirname(__file__)
    input_stream = FileStream(directory+"/test/test_mixed_indentation.py", 'utf-8')
    lexer = Python3Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Python3Parser(stream)
    syntaxErrorListener = SyntaxErrorListener([0, 0])
    parser.addErrorListener(syntaxErrorListener)
    tree = parser.file_input()
    visitor = AntiVisitor([0, 0])
    visitor.visit(tree)
    print('hola')


if __name__ == '__main__':
    main(sys.argv)
