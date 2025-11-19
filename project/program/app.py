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
st.write("Escribe tu código en el área de entrada o sube un archivo, presiona **Run** para analizarlo, y revisa el resultado o los errores en la salida.")

# Inicializar el código de entrada
if 'code_input' not in st.session_state:
    st.session_state.code_input = ""

# Crear dos columnas para la entrada
col1, col2 = st.columns(2)

with col1:
    st.subheader("Entrada por texto")
    text_input = st.text_area(
        "Escribe tu código aquí:",
        value=st.session_state.code_input,
        height=300,
        placeholder="x = 10;\n"
    )
    st.session_state.code_input = text_input

with col2:
    st.subheader("Subir archivo")
    uploaded_file = st.file_uploader("Elige un archivo", type=['cps', 'txt'], key="file_uploader")

    if uploaded_file is not None:
        # Leer contenido del archivo
        file_contents = uploaded_file.getvalue().decode("utf-8")
        if st.session_state.code_input != file_contents:
            st.session_state.code_input = file_contents
            st.session_state.last_uploaded_file = uploaded_file.name
            st.success(f"Archivo cargado: {uploaded_file.name}")
    else:
        # Si antes había un archivo y ahora no hay ninguno, limpiar todo
        if "last_uploaded_file" in st.session_state:
            st.session_state.code_input = ""
            del st.session_state.last_uploaded_file
            st.info("Archivo quitado. Área de texto vaciada.")


# Botón para ejecutar el código
if st.button("Run"):
    if st.session_state.code_input and st.session_state.code_input.strip():
        try:
            # Procesar el código con ANTLR
            input_stream = InputStream(st.session_state.code_input)
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
                    ir = ir_gen.generate(ast)
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
        st.warning("Por favor, escribe algo de código o sube un archivo antes de presionar Run.")

# Espacio para mostrar el resultado o errores
st.subheader("Salida")
st.write("Aquí se mostrarán los resultados o errores después de ejecutar el código.")