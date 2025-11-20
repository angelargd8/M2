# ===============================================================
# Manejo de variables globales con etiquetas seguras
# Cada global se renombra como g_<name> para evitar conflicto
# con registros ($a0, $t1, etc.) en SPIM.
# ===============================================================

from AstNodes import VarDecl, FloatLiteral, IntLiteral, BooleanLiteral, StringLiteral, ListLiteral

class MIPSVar:
    def __init__(self, codegen):
        self.cg = codegen

        # Para impresión de arreglos
        self.array_info = {}

    # ------------ helpers ------------

    def _eval_int_like(self, expr):
        if isinstance(expr, IntLiteral):
            return int(expr.value)
        if isinstance(expr, BooleanLiteral):
            return 1 if expr.value else 0
        raise Exception(f"MIPSVar: inicializador entero no soportado: {expr}")

    def _eval_float(self, expr):
        if isinstance(expr, FloatLiteral):
            return float(expr.value)
        raise Exception(f"MIPSVar: inicializador float no soportado: {expr}")

    def _eval_string(self, expr):
        if isinstance(expr, StringLiteral):
            return expr.value
        return None

    def _is_list_of_ints(self, lit: ListLiteral):
        return all(isinstance(e, (IntLiteral, BooleanLiteral)) for e in lit.elements)

    def _is_list_of_list_of_ints(self, lit: ListLiteral):
        return all(isinstance(e, ListLiteral) and self._is_list_of_ints(e)
                   for e in lit.elements)

    # ------------ registro global ------------

    def register_global(self, name, sym):

        # etiqueta segura g_name
        safe = f"g_{name}"
        sym.mips_label = safe    # guardar el label real usado en MIPS

        typ = sym.type.name
        decl = sym.decl_node

        init_expr = None
        if isinstance(decl, VarDecl):
            init_expr = decl.init

        # ===== int =====
        if typ == "int":
            if isinstance(init_expr, (IntLiteral, BooleanLiteral)):
                val = self._eval_int_like(init_expr)
                self.cg.global_data.append(f"{safe}: .word {val}")
            else:
                self.cg.global_data.append(f"{safe}: .word 0")
            return

        # ===== float =====
        if typ == "float":
            if isinstance(init_expr, FloatLiteral):
                val = self._eval_float(init_expr)
                self.cg.global_data.append(f"{safe}: .float {val}")
            else:
                self.cg.global_data.append(f"{safe}: .float 0.0")
            return

        # ===== bool =====
        if typ == "bool":
            if isinstance(init_expr, (IntLiteral, BooleanLiteral)):
                val = self._eval_int_like(init_expr)
                self.cg.global_data.append(f"{safe}: .word {val}")
            else:
                self.cg.global_data.append(f"{safe}: .word 0")
            return

        # ===== string =====
        if typ == "string":
            if isinstance(init_expr, StringLiteral):
                text = self._eval_string(init_expr)
                label = self.cg._add_string_literal(f"\"{text}\"")
                self.cg.global_data.append(f"{safe}: .word {label}")
            else:
                self.cg.global_data.append(f"{safe}: .word 0")
            return

        # ===== Arrays 1D/2D =====
        if isinstance(init_expr, ListLiteral):

            # 1D ints
            if self._is_list_of_ints(init_expr):
                vals = [self._eval_int_like(e) for e in init_expr.elements]
                vals_str = ", ".join(str(v) for v in vals)
                self.cg.global_data.append(f"{safe}: .word {vals_str}")
                self.array_info[name] = ("1D", vals)
                return

            # 1D strings
            if all(isinstance(e, StringLiteral) for e in init_expr.elements):
                labels = []
                for e in init_expr.elements:
                    text = self._eval_string(e)
                    lbl = self.cg._add_string_literal(f"\"{text}\"")
                    labels.append(lbl)
                self.cg.global_data.append(f"{safe}: .word {', '.join(labels)}")
                self.array_info[name] = ("1D_STR", labels)
                return

            # 1D floats
            if all(isinstance(e, FloatLiteral) for e in init_expr.elements):
                vals = [self._eval_float(e) for e in init_expr.elements]
                vals_str = ", ".join(str(v) for v in vals)
                self.cg.global_data.append(f"{safe}: .float {vals_str}")
                self.array_info[name] = ("1D_FLOAT", vals)
                return

            # 2D ints
            if self._is_list_of_list_of_ints(init_expr):
                row_labels = []
                rows = []

                for i, row in enumerate(init_expr.elements):
                    vals = [self._eval_int_like(x) for x in row.elements]
                    rows.append(vals)

                    row_label = f"{safe}_row_{i}"
                    self.cg.global_data.append(
                        f"{row_label}: .word {', '.join(str(x) for x in vals)}"
                    )
                    row_labels.append(row_label)

                self.cg.global_data.append(f"{safe}: .word {', '.join(row_labels)}")
                self.array_info[name] = ("2D", rows)
                return

            raise Exception("MIPSVar: tipo de array no soportado")

        # default sin inicializador
        self.cg.global_data.append(f"{safe}: .word 0")
