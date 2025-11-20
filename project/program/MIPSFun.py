# Módulo para manejo de funciones en MIPS:
# - prolog / epilog
# - param / call
# - load / store con FP[offset]
# - ret (con caso especial para main)

class MIPSFun:
    def __init__(self, codegen):
        self.cg = codegen
        self.current_func = None

    # ----------------------------------------------------
    # Helpers FP[offset]
    # ----------------------------------------------------
    def is_fp_addr(self, addr):
        """Detecta direcciones tipo FP[16]."""
        return isinstance(addr, str) and addr.startswith("FP[")

    def get_fp_offset(self, addr):
        return int(addr[3:-1])

    # ----------------------------------------------------
    # PROLOG / EPILOG
    # ----------------------------------------------------
    def emit_prolog(self, func_label):
        """Prolog estándar para una función."""
        self.current_func = func_label
        cg = self.cg
        cg.emit("    # ---- PROLOG ----")
        cg.emit("    addi $sp, $sp, -8")
        cg.emit("    sw $fp, 4($sp)")
        cg.emit("    sw $ra, 0($sp)")
        cg.emit("    move $fp, $sp")
        # Aquí podrías reservar espacio extra para locales:
        # if cg.symtab and hasattr(cg.symtab, 'get_frame_size'):
        #     fs = cg.symtab.get_frame_size(func_label)
        #     if fs > 0:
        #         cg.emit(f"    addi $sp, $sp, -{fs}")

    def emit_epilog(self):
        """Epilog estándar."""
        cg = self.cg
        cg.emit("    # ---- EPILOG ----")
        cg.emit("    move $sp, $fp")
        cg.emit("    lw $ra, 0($sp)")
        cg.emit("    lw $fp, 4($sp)")
        cg.emit("    addi $sp, $sp, 8")
        cg.emit("    jr $ra")

    # ----------------------------------------------------
    # PARAM / CALL
    # ----------------------------------------------------
    def emit_param(self, t_arg):
        """
        param t_arg:
          - evalúa el temporal t_arg
          - lo pushea a la pila como argumento
        """
        cg = self.cg
        reg = cg.tm.get_reg(t_arg)
        cg._load(t_arg, reg)
        cg.emit("    addi $sp, $sp, -4")
        cg.emit(f"    sw {reg}, 0($sp)")

    def emit_call(self, func_label, argc, t_res):
        """
        call func_label, argc, t_res
        (por ahora ignoramos argc en MIPS puro, pero el IR lo lleva
         por coherencia, ya que los args están en la pila)
        """
        cg = self.cg
        cg.emit(f"    jal {func_label}")
        # resultado de la función en $v0
        reg_r = cg.tm.get_reg(t_res)
        cg.emit(f"    move {reg_r}, $v0")

    # ----------------------------------------------------
    # LOAD / STORE con FP[offset]
    # ----------------------------------------------------
    def emit_load(self, addr, t_dst):
        """
        load FP[offset] -> t_dst
        """
        cg = self.cg
        off = self.get_fp_offset(addr)
        reg = cg.tm.get_reg(t_dst)
        cg.emit(f"    lw {reg}, {off}($fp)")

    def emit_store(self, t_src, addr):
        """
        store t_src -> FP[offset]
        """
        cg = self.cg
        off = self.get_fp_offset(addr)
        reg = cg.tm.get_reg(t_src)
        cg._load(t_src, reg)
        cg.emit(f"    sw {reg}, {off}($fp)")

    # ----------------------------------------------------
    # RETURN
    # ----------------------------------------------------
    def emit_ret(self, t_value):
        """
        ret t_value  /  ret (sin valor)
        - si no es main: hace epilog + jr $ra
        - si es main: termina el programa con syscall 10
        """
        cg = self.cg

        # Si hay valor de retorno, ponerlo en $v0
        if t_value is not None and t_value != "0":
            reg = cg.tm.get_reg(t_value)
            cg._load(t_value, reg)
            cg.emit(f"    move $v0, {reg}")

        # main termina el programa
        if self.current_func == "main":
            cg.emit("    li $v0, 10")
            cg.emit("    syscall")
        else:
            self.emit_epilog()
