# Módulo para imprimir:
# - strings literales
# - strings globales
# - strings dinámicos creados por MIPSStrings
# - enteros
# - booleanos

class MIPSPrint:
    def __init__(self, codegen):
        """
        codegen: referencia al generador principal MIPSCodeGen
        """
        self.cg = codegen


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

        # salto de línea
        self.cg.emit("    la $a0, nl")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")


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

        # salto de línea
        self.cg.emit("    la $a0, nl")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")


    # ============================================================
    # PRINT INT (literal inmediato)
    # ============================================================
    def print_int_imm(self, value):
        self.cg.emit(f"    # print int literal: {value}")
        self.cg.emit(f"    li $a0, {value}")
        self.cg.emit("    li $v0, 1")
        self.cg.emit("    syscall")

        # salto de línea
        self.cg.emit("    la $a0, nl")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")


    # ============================================================
    # PRINT BOOLEAN
    # ============================================================
    def print_bool(self, value):
        num = 1 if value else 0
        self.print_int_imm(num)


    def print_global_var(self, name):
        sym = self.cg.symtab.global_scope.symbols[name]
        t = sym.type.name

        # STRING GLOBAL: greeting: .word str_0
        if t == "string":
            self.cg.emit(f"    la $t0, {name}")
            self.cg.emit("    lw $a0, 0($t0)")
            self.cg.emit("    li $v0, 4")
            self.cg.emit("    syscall")
            self.cg.emit("    la $a0, nl")
            self.cg.emit("    li $v0, 4")
            self.cg.emit("    syscall")
            return

        # INT GLOBAL
        if t == "int":
            self.cg.emit(f"    la $t0, {name}")
            self.cg.emit("    lw $a0, 0($t0)")
            self.cg.emit("    li $v0, 1")
            self.cg.emit("    syscall")
            self.cg.emit("    la $a0, nl")
            self.cg.emit("    li $v0, 4")
            self.cg.emit("    syscall")
            return

        # BOOLEAN GLOBAL
        if t == "bool":
            self.cg.emit(f"    la $t0, {name}")
            self.cg.emit("    lw $a0, 0($t0)")
            self.cg.emit("    li $v0, 1")
            self.cg.emit("    syscall")
            self.cg.emit("    la $a0, nl")
            self.cg.emit("    li $v0, 4")
            self.cg.emit("    syscall")
            return

        # ARRAY → implementar después
        raise Exception(f"print_global_var: tipo no soportado {t}")

    def print_int_reg(self, t):
        value = self.cg.temp_int[t]   # ←  guardar el entero real
        self.cg.emit(f"    # print int from temp {t} = {value}")
        self.cg.emit(f"    li $a0, {value}")
        self.cg.emit("    li $v0, 1")
        self.cg.emit("    syscall")
        self.cg.emit("    la $a0, nl")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")


    # ============================================================
    # DISPATCH PRINCIPAL DE PRINT
    # ============================================================
    def handle_print(self, arg):

        # VARIABLES GLOBALES
        if arg in self.cg.symtab.global_scope.symbols:
            return self.print_global_var(arg)

        # STRING LITERAL
        label = self.cg.temp_string.get(arg)
        if label and label.startswith("str_"):
            return self.print_string(label)

        # STRING DINÁMICO
        if arg in self.cg.temp_ptr:
            return self.print_dynamic_string(arg)
        
        # INT 
        if arg in self.cg.temp_int:
            return self.print_int_reg(arg)

        

        raise Exception(f"MIPSPrint: no se puede imprimir {arg}")