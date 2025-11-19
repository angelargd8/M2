# Manejo de variables globales y locales.
# Se integra con SymbolTable para obtener:
# - nombre
# - tipo (int, string, boolean, array, matrix)
# - valores iniciales

class MIPSVar:
    def __init__(self, cg):
        self.cg = cg  # referencia al MIPSCodeGen
        self.global_vars = {}  # nombre → tipo

    # ============================================================
    # REGISTRO DE VARIABLES GLOBALES
    # ============================================================
    def register_global(self, name, symbol):
        t = symbol.type.name
        decl = symbol.decl_node   # VarDecl original en el AST
        init = getattr(decl, "init", None)

        # ========== INTEGER ==========
        if t == "int":
            if init and init.__class__.__name__ == "IntLiteral":
                self.cg.global_data.append(f"{name}: .word {init.value}")
            else:
                self.cg.global_data.append(f"{name}: .word 0")
            return

        # ========== BOOLEAN ==========
        if t == "bool":
            if init and init.__class__.__name__ == "BooleanLiteral":
                v = 1 if init.value else 0
                self.cg.global_data.append(f"{name}: .word {v}")
            else:
                self.cg.global_data.append(f"{name}: .word 0")
            return

        # ========== STRING ==========
        if t == "string":
            if init and init.__class__.__name__ == "StringLiteral":
                literal = init.value
                label = self.cg._add_string_literal(f"\"{literal}\"")
                self.cg.global_data.append(f"{name}: .word {label}")
            else:
                self.cg.global_data.append(f"{name}: .word 0")
            return

        # ========== ARRAY INT[] ==========
        if t == "list" and symbol.type.elem.name == "int":
            if init and init.__class__.__name__ == "ListLiteral":
                values = [ e.value for e in init.elements ]
                content = ", ".join(str(v) for v in values)
                self.cg.global_data.append(f"{name}: .word {content}")
            else:
                self.cg.global_data.append(f"{name}: .word 0")
            return

        # ========== ARRAY 2D int[][] ==========
        if t == "list" and symbol.type.elem.name == "list":
            row_labels = []
            if init and init.__class__.__name__ == "ListLiteral":
                for i, row in enumerate(init.elements):
                    row_label = f"{name}_row_{i}"
                    row_labels.append(row_label)
                    vals = ", ".join(str(e.value) for e in row.elements)
                    self.cg.global_data.append(f"{row_label}: .word {vals}")

                pointer_list = ", ".join(row_labels)
                self.cg.global_data.append(f"{name}: .word {pointer_list}")
            else:
                self.cg.global_data.append(f"{name}: .word 0")
            return

        raise Exception(f"MIPSVar: tipo no soportado: {t}")

    # ============================================================
    # GENERAR CÓDIGO PARA CARGAR UNA VARIABLE GLOBAL
    # ============================================================
    def load_global(self, name, dest_reg):
        """Cargar variable global (nombre) en registro dest_reg."""
        self.cg.emit(f"    la {dest_reg}, {name}")  # dirección
        self.cg.emit(f"    lw {dest_reg}, 0({dest_reg})")

    # ============================================================
    # GUARDAR DESDE UN REGISTRO A VARIABLE GLOBAL
    # ============================================================
    def store_global(self, name, src_reg):
        self.cg.emit(f"    la $t0, {name}")
        self.cg.emit(f"    sw {src_reg}, 0($t0)")
