# Módulo para imprimir:
# - strings literales
# - strings globales
# - strings dinámicos creados por MIPSStrings
# - enteros
# - booleanos
# - arrays globales (1D y 2D) usando vars_mod.array_info

class MIPSPrint:
    def __init__(self, codegen):
        """
        codegen: referencia al generador principal MIPSCodeGen
        """
        self.cg = codegen

    # ----------------- helpers básicos -----------------

    def _newline(self):
        self.cg.emit("    la $a0, nl")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")

    def _print_char(self, ch: str):
        """Imprime un solo carácter con syscall 11."""
        self.cg.emit(f"    li $a0, {ord(ch)}")
        self.cg.emit("    li $v0, 11")
        self.cg.emit("    syscall")

    def _raw_print(self, label):
        """Imprime una string en .data por label (sin salto de línea)."""
        self.cg.emit(f"    la $a0, {label}")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")

    # ----------------- arrays globales -----------------

    def _print_global_array_1d(self, name, values):
        """
        values: lista de ints, viene de vars_mod.array_info[name][1]
        """
        self.cg.emit(f"    # print 1D global array {name}")

        # [
        self._print_char('[')

        for i, v in enumerate(values):
            # número
            self.cg.emit(f"    li $a0, {v}")
            self.cg.emit("    li $v0, 1")
            self.cg.emit("    syscall")

            # coma+espacio si no es el último
            if i != len(values) - 1:
                self._print_char(',')
                self._print_char(' ')

        # ]
        self._print_char(']')
        self._newline()

    def _print_global_array_2d(self, name, rows):
        """
        rows: lista de listas de ints
        """
        self.cg.emit(f"    # print 2D global array {name}")

        # outer [
        self._print_char('[')

        for r_i, row in enumerate(rows):
            # [
            self._print_char('[')

            for c_i, v in enumerate(row):
                self.cg.emit(f"    li $a0, {v}")
                self.cg.emit("    li $v0, 1")
                self.cg.emit("    syscall")

                if c_i != len(row) - 1:
                    self._print_char(',')
                    self._print_char(' ')

            # ]
            self._print_char(']')

            if r_i != len(rows) - 1:
                self._print_char(',')
                self._print_char(' ')

        # ]
        self._print_char(']')
        self._newline()

    # ============================================================
    # PRINT STRING (literal o label en .data)
    # ============================================================
    def print_string(self, label):
        """
        label: str_X en .data
        """
        self.cg.emit(f"    # print string (literal/global): {label}")
        self.cg.emit(f"    la $a0, {label}")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")
        self._newline()

    # ============================================================
    # PRINT STRING DINÁMICO (puntero)
    # ============================================================
    def print_dynamic_string(self, t):
        """
        t : nombre del temporal (t5, t7, etc.)
        cg.ptr_table[t] contiene el registro donde está el puntero real.
        """
        reg = self.cg.ptr_table[t]   # ← puntero real en un registro

        self.cg.emit(f"    # print dynamic string in {t}")
        self.cg.emit(f"    move $a0, {reg}")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")
        self._newline()

    # ============================================================
    # PRINT INT (literal inmediato)
    # ============================================================
    def print_int_imm(self, value):
        self.cg.emit(f"    # print int literal: {value}")
        self.cg.emit(f"    li $a0, {value}")
        self.cg.emit("    li $v0, 1")
        self.cg.emit("    syscall")
        self._newline()

    # ============================================================
    # PRINT BOOLEAN
    # ============================================================
    def print_bool(self, value):
        num = 1 if value else 0
        self.print_int_imm(num)

    # ============================================================
    # PRINT GLOBAL VAR (int, bool, string, array)
    # ============================================================
    def print_global_var(self, name):
        # Primero: ¿es un array global registrado en vars_mod.array_info?
        info = getattr(self.cg.vars_mod, "array_info", {}).get(name)
        if info is not None:
            kind, data = info  # kind = "1D" o "2D"
            if kind == "1D":
                return self._print_global_array_1d(name, data)
            elif kind == "2D":
                return self._print_global_array_2d(name, data)
            # fallback raro: solo imprimir [array]
            self.cg.emit("    # array global sin meta conocida")
            self._print_char('[')
            self._print_char(']')
            self._newline()
            return

        # Si no es array, usamos el tipo de la tabla de símbolos
        sym = self.cg.symtab.global_scope.symbols[name]
        t = sym.type.name

        # STRING GLOBAL: greeting: .word str_0
        if t == "string":
            self.cg.emit(f"    la $t0, {name}")
            self.cg.emit("    lw $a0, 0($t0)")
            self.cg.emit("    li $v0, 4")
            self.cg.emit("    syscall")
            self._newline()
            return

        # INT GLOBAL
        if t == "int":
            self.cg.emit(f"    la $t0, {name}")
            self.cg.emit("    lw $a0, 0($t0)")
            self.cg.emit("    li $v0, 1")
            self.cg.emit("    syscall")
            self._newline()
            return

        # BOOLEAN GLOBAL
        if t == "bool":
            self.cg.emit(f"    la $t0, {name}")
            self.cg.emit("    lw $a0, 0($t0)")
            self.cg.emit("    li $v0, 1")
            self.cg.emit("    syscall")
            self._newline()
            return

        raise Exception(f"print_global_var: tipo no soportado {t} para {name}")

    # ============================================================
    # PRINT INT DESDE TEMPORAL
    # ============================================================
    def print_int_reg(self, t):
        value = self.cg.temp_int[t]   # entero conocido en compilación
        self.cg.emit(f"    # print int from temp {t} = {value}")
        self.cg.emit(f"    li $a0, {value}")
        self.cg.emit("    li $v0, 1")
        self.cg.emit("    syscall")
        self._newline()

    # ============================================================
    # DISPATCH PRINCIPAL DE PRINT
    # ============================================================
    def handle_print(self, arg):

        # VARIABLES GLOBALES
        if arg in self.cg.symtab.global_scope.symbols:
            return self.print_global_var(arg)

        # STRING LITERAL (temporal que referencia str_X)
        label = self.cg.temp_string.get(arg)
        if label and label.startswith("str_"):
            return self.print_string(label)

        # STRING DINÁMICO (puntero)
        if arg in self.cg.temp_ptr:
            return self.print_dynamic_string(arg)

        # ENTERO EN TEMPORAL
        if arg in self.cg.temp_int:
            return self.print_int_reg(arg)

        raise Exception(f"MIPSPrint: no se puede imprimir {arg}")
