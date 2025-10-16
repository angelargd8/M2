import streamlit as st
from antlr4 import *
from gen.CompiscriptLexer import CompiscriptLexer
from gen.CompiscriptParser import CompiscriptParser
from AstBuilder import AstBuilder
from SemanticAnalyzer import SemanticAnalyzer
from IRGenerator import IRGenerator
from IR import to_quads

# Configurar el diseño en formato "wide"
st.set_page_config(layout="wide")

# Título de la aplicación
st.title("IDE")

# Descripción
st.write("Escribe tu código en el área de entrada, presiona **Run** para analizarlo, y revisa el resultado o los errores en la salida.")

# Área de entrada para el código
code_input = st.text_area("Escribe tu código aquí:", height=300, placeholder="x = 10;\n")

# Botón para ejecutar el código
if st.button("Run"):
    if code_input.strip():  # Verifica que el área de entrada no esté vacía
        try:
            # Procesar el código con ANTLR
            input_stream = InputStream(code_input)
            lexer = CompiscriptLexer(input_stream)
            stream = CommonTokenStream(lexer)
            parser = CompiscriptParser(stream)
            tree = parser.program()

            # Verificar errores de sintaxis
            syntax_errors = parser.getNumberOfSyntaxErrors()
            if syntax_errors > 0:
                st.error(f"Se encontraron {syntax_errors} errores de sintaxis.")
            else:
                # Construir el AST
                ast = AstBuilder().visit(tree)

                # Análisis semántico
                analyzer = SemanticAnalyzer()
                analyzer.collect_signatures(ast)  # Pasada 1
                semantic_errors = analyzer.check(ast)  # Pasada 2

                if semantic_errors:
                    st.error("Errores semánticos encontrados:")
                    for error in semantic_errors:
                        st.write(f"- {error}")
                else:
                    st.success("¡Chequeo semántico sin errores!")
                    
                    # Generación de código intermedio/tres direcciones
                    ir_gen = IRGenerator()
                    ir = ir_gen.generate(tree)
                    quads = to_quads(ir)
                    
                    # Guardar el TAC en un archivo
                    with open("./output/program.tac", "w") as f:
                        for i in quads:
                            f.write(repr(i) + "\n")
                    
                    st.success("Código intermedio (TAC) generado y guardado en output/program.tac")
                    st.write("Árbol de análisis generado con éxito.")

        except Exception as e:
            st.error(f"Error al procesar el código: {e}")
    else:
        st.warning("Por favor, escribe algo de código antes de presionar Run.")

# Espacio para mostrar el resultado o errores
st.subheader("Salida")
st.write("Aquí se mostrarán los resultados o errores después de ejecutar el código.")