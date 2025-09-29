import sys
from antlr4 import *
from gen.CompiscriptLexer import CompiscriptLexer
from gen.CompiscriptParser import CompiscriptParser
from AstBuilder import AstBuilder
from AstVisualization import render_ast
from SemanticAnalyzer import SemanticAnalyzer

def parse(argv):
    input_stream = FileStream(argv[1], encoding='utf-8')
    lexer = CompiscriptLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CompiscriptParser(stream)
    tree = parser.program()

    errs = parser.getNumberOfSyntaxErrors()
    if errs > 0:
        print(f"Se encontraron {errs} errores de sintaxis.")
        sys.exit(1)

    return tree



def main(argv):
    
    tree = parse(argv)
    # AST - Abstract Syntax Tree
    ast = AstBuilder().visit(tree)
    # print(ast)
    render_ast(ast, "./output/ast")
    path = "./output/ast.png"
    print("la foto de AST esta en la carpeta output:", path)

    analyzer = SemanticAnalyzer()
    analyzer.collect_signatures(ast)       # Pasada 1
    errors = analyzer.check(ast)           # Pasada 2

    if errors:
        print("Errores semánticos:")
        for e in errors:
            print("  -", e)

    else:
        print("Chequeo semántico sin errores!")


    

if __name__ == '__main__':
    main(sys.argv)