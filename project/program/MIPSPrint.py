# Módulo encargado de generar código MIPS para la instrucción "print".

class MIPSPrint:
    def __init__(self, codegen):
        """
        codegen: referencia al generador principal MIPSCodeGen
        """
        self.cg = codegen

    # ---------------- PRINT STRING ----------------
    def print_string(self, label):
        """
        label: label en .data de la string (ej: 'str_0')
        """
        self.cg.emit(f"    # print string: {label}")
        self.cg.emit(f"    la $a0, {label}")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")

        # salto de línea
        self.cg.emit("    la $a0, nl")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")

    # ---------------- PRINT INT (literal) ----------------
    def print_int_imm(self, value):
        """
        value: entero inmediato (ej: 1, 42)
        """
        self.cg.emit(f"    # print int literal: {value}")
        self.cg.emit(f"    li $a0, {value}")
        self.cg.emit("    li $v0, 1")
        self.cg.emit("    syscall")

        # salto de línea
        self.cg.emit("    la $a0, nl")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")

    def print_dynamic_string(self, t):
        self.cg.emit(f"    # print dynamic string in {t}")
        self.cg.emit("    move $a0, $v1")      # v1 holds pointer from concat
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")
        self.cg.emit("    la $a0, nl")
        self.cg.emit("    li $v0, 4")
        self.cg.emit("    syscall")

    # ---------------- API PRINCIPAL ----------------
    def handle_print(self, arg):

        # CASE 1: string literal o label en .data
        label = self.cg.temp_string.get(arg)
        if label is not None:
            if label.startswith("str_"):
                return self.print_string(label)
        
        # CASE 2: pointer resultado de concatenación dinámica
        if arg in self.cg.temp_ptr:
            return self.print_dynamic_string(arg)

        # CASE 3: entero literal
        if arg in self.cg.temp_int:
            return self.print_int_imm(self.cg.temp_int[arg])

        raise Exception(f"MIPSPrint: tipo no soportado en print: {arg}")
