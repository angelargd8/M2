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
        ir = ir_gen.generate(tree)
        print("== IR (TAC) ==")
       
        print("\n== quads ==")
        quads = to_quads(ir)
        print_quads(quads)

        # Guardar el código intermedio en un archivo
        with open("./output/program.tac", "w") as f:
            for i in quads:
                f.write(repr(i) + "\n")
        # -------------


        # -- generar mips --
        mips_gen = MIPSCodeGen(quads, symtab=analyzer.symtab)
        mips_code = mips_gen.generate()

        with open("./output/program.s", "w") as f: 
            f.write(mips_code)
        
        print("\ncodigo mips guardado en ./output/program.s")

        # -- cargar runtime --
        try:
            with open("./runtime.asm", "r") as f:
                runtime_code = f.read()
        except FileNotFoundError:
            print("ERROR: No se encontró ./runtime.asm")
            sys.exit(1)

        # combinar runtime con el programa
        final_code = runtime_code + "\n\n# ===== Compiscript Program =====\n\n" + mips_code

        # Guardar final.s
        with open("./output/final.s", "w") as f:
            f.write(final_code)

        print(">> Archivo final listo para SPIM/MARS: ./output/final.s")


if __name__ == '__main__':
    main(sys.argv)