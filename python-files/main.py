from core.lexer import lex
from core.parser import Parser
from core.interpreter import Interpreter

if __name__ == '__main__':
    code = open('test.xo', 'r').read()

    tokens = lex(code) # лексер
    parser = Parser(tokens)
    ast = parser.parse() # ast дерево

    interpreter = Interpreter()
    interpreter.eval(ast)
