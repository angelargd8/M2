# Manejo de variables globales y locales.
# Se integra con SymbolTable para obtener:
# - nombre
# - tipo (int, string, boolean, array, matrix)
# - valores iniciales
# Construye la sección .data para variables globales
# Usando el AST en sym.decl_node.init
# Además expone array_info para que MIPSPrint pueda imprimir arrays globales.

from AstNodes import VarDecl, IntLiteral, BooleanLiteral, StringLiteral, ListLiteral

class MIPSVar:
    def __init__(self, codegen):
        self.cg = codegen

        # Para que MIPSPrint pueda saber cómo imprimir un array global
        # array_info[name] = ("1D", [1,2,3,...])
        # array_info[name] = ("2D", [[1,2],[3,4],...])
        self.array_info = {}

    # ---------------- helpers ----------------

    def _eval_int_like(self, expr):
        if isinstance(expr, IntLiteral):
            return int(expr.value)
        if isinstance(expr, BooleanLiteral):
            return 1 if expr.value else 0
        raise Exception(f"MIPSVar: inicializador entero no soportado: {expr}")

    def _eval_string(self, expr):
        if isinstance(expr, StringLiteral):
            return expr.value
        return None

    def _is_list_of_ints(self, lit: ListLiteral):
        return all(isinstance(e, IntLiteral) or isinstance(e, BooleanLiteral)
                   for e in lit.elements)

    def _is_list_of_list_of_ints(self, lit: ListLiteral):
        return all(
            isinstance(elem, ListLiteral) and self._is_list_of_ints(elem)
            for elem in lit.elements
        )

    # ---------------- registro global ----------------

    def register_global(self, name, sym):

        typ = sym.type.name
        decl = sym.decl_node

        init_expr = None
        if isinstance(decl, VarDecl):
            init_expr = decl.init

        # ===== int =====
        if typ == "int":
            val = self._eval_int_like(init_expr) if init_expr else 0
            self.cg.global_data.append(f"{name}: .word {val}")
            return

        # ===== bool =====
        if typ == "bool":
            val = self._eval_int_like(init_expr) if init_expr else 0
            self.cg.global_data.append(f"{name}: .word {val}")
            return

        # ===== string =====
        if typ == "string":
            if init_expr:
                text = self._eval_string(init_expr)
                label = self.cg._add_string_literal(f"\"{text}\"")
                self.cg.global_data.append(f"{name}: .word {label}")
            else:
                self.cg.global_data.append(f"{name}: .word 0")
            return

        # ===== array (1D or 2D) =====
        if isinstance(init_expr, ListLiteral):

            # 1D array
            if self._is_list_of_ints(init_expr):
                vals = [self._eval_int_like(e) for e in init_expr.elements]
                vals_str = ", ".join(str(v) for v in vals)
                self.cg.global_data.append(f"{name}: .word {vals_str}")

                # Guardamos meta para imprimir
                self.array_info[name] = ("1D", vals)
                return

            # 2D array
            if self._is_list_of_list_of_ints(init_expr):
                row_labels = []
                rows = []

                for i, row in enumerate(init_expr.elements):
                    row_vals = [self._eval_int_like(e) for e in row.elements]
                    rows.append(row_vals)

                    row_label = f"{name}_row_{i}"
                    self.cg.global_data.append(
                        f"{row_label}: .word {', '.join(str(x) for x in row_vals)}"
                    )
                    row_labels.append(row_label)

                self.cg.global_data.append(
                    f"{name}: .word " + ", ".join(row_labels)
                )

                self.array_info[name] = ("2D", rows)
                return

            raise Exception(
                f"MIPSVar: tipo de array no soportado para global '{name}'"
            )

        # Sin inicializador → solo una palabra
        if typ in ("array", "list"):
            self.cg.global_data.append(f"{name}: .word 0")
            return

        # Default
        self.cg.global_data.append(f"{name}: .word 0")
