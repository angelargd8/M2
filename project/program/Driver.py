import sys
from antlr4 import *
from gen.CompiscriptLexer import CompiscriptLexer
from gen.CompiscriptParser import CompiscriptParser
from AstBuilder import AstBuilder
from AstVisualization import render_ast
from SemanticAnalyzer import SemanticAnalyzer
from codeGen import CodeGen
from IR import print_ir, to_quads, print_quads, print_ir_modern
from IRGenerator import IRGenerator

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
    # construccion del AST - Abstract Syntax Tree
    ast = AstBuilder().visit(tree)
    # print(ast)
    render_ast(ast, "./output/ast")
    path = "./output/ast.png"
    print("la foto de AST esta en la carpeta output:", path)

    # analisis semantico
    analyzer = SemanticAnalyzer()


    analyzer.collect_signatures(ast)       # Pasada 1
    errors = analyzer.check(ast)           # Pasada 2

    if errors:
        print(">> Errores semánticos:")
        for e in errors:
            print("  -", e)

    else:
        print(">> Chequeo semántico sin errores!")
        
        # Generación de código intermedio/tres direcciones
        ir_gen = IRGenerator(symtab=analyzer.symtab)
        # genera los quads recorriendo el AST
        ir = ir_gen.generate(tree)
        print("== IR (TAC) ==")
        # #------ esta parte es solo para ver bonito el TAC
        # # realmente no es necesario y se puede comentar
        # # es para tener idea para ver el tac sin garbage colector
        # gen_print = CodeGen(symtab=analyzer.symtab)
        # ir_print = gen_print.generate(ast)
        # print_ir(ir_print, symtab=analyzer.symtab)
        # #----------------------------------------------------

        print("\n== quads ==")
        quads = to_quads(ir)
        print_quads(quads)

        # Guardar el código intermedio en un archivo
        with open("./output/program.tac", "w") as f:
            for i in quads:
                f.write(repr(i) + "\n")


if __name__ == '__main__':
    main(sys.argv)