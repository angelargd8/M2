import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


import pytest
from antlr4 import InputStream, CommonTokenStream
from gen.CompiscriptLexer import CompiscriptLexer
from gen.CompiscriptParser import CompiscriptParser
from IRGenerator import IRGenerator
from SymbolTable import SymbolTable


@pytest.fixture
def build_ir():
    # Construye el IR (quads) 
    def _build_ir(source_code: str):
        input_stream = InputStream(source_code)
        lexer = CompiscriptLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = CompiscriptParser(tokens)
        tree = parser.program()
        symtab = SymbolTable()
        irgen = IRGenerator(symtab)
        return irgen.generate(tree)
    return _build_ir
