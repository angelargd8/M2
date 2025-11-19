import sys
from antlr4 import *
from gen.CompiscriptLexer import CompiscriptLexer
from gen.CompiscriptParser import CompiscriptParser
from AstBuilder import AstBuilder
from AstVisualization import render_ast
from SemanticAnalyzer import SemanticAnalyzer
from IR import to_quads, print_quads
from IRGenerator import IRGenerator
from MIPSCodeGen import MIPSCodeGen

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
    
    # --- parse to ast ----
    tree = parse(argv)
    # construccion del AST - Abstract Syntax Tree
    ast = AstBuilder().visit(tree)
    # print(ast)
    render_ast(ast, "./output/ast")
    path = "./output/ast.png"
    print("la foto de AST esta en la carpeta output:", path)

    # -----------------

    # --- analisis semantico ---
    analyzer = SemanticAnalyzer()


    analyzer.collect_signatures(ast)       # Pasada 1
    errors = analyzer.check(ast)           # Pasada 2

    if errors:
        print(">> Errores semánticos:")
        for e in errors:
            print("  -", e)

    else:
        print(">> Chequeo semántico sin errores!")

    # --------------------

        # --- IR (tac) ---
        # Generación de código intermedio/tres direcciones
        ir_gen = IRGenerator(symtab=analyzer.symtab)
        # genera los quads recorriendo el AST
        ir = ir_gen.generate(ast)
        print("== IR (TAC) ==")
       
        print("\n== quads ==")
        quads = ir
        print_quads(to_quads(quads))

        # Guardar el código intermedio en un archivo
        with open("./output/program.tac", "w") as f:
            for i in quads:
                f.write(repr(i) + "\n")
        # -------------

        # -- generar mips --
        mips_gen = MIPSCodeGen(quads, analyzer.symtab)
        mips_code = mips_gen.generate()

        final_code = "\n\n# ===== Compiscript Program =====\n\n" + mips_code


        # Guardar final.s
        with open("./output/final.s", "w") as f:
            f.write(final_code)

        print(">> Archivo final en: ./output/final.s")


if __name__ == '__main__':
    main(sys.argv)