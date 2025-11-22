# Módulo para manejo de funciones en MIPS:
# - prolog / epilog
# - param / call
# - load / store con FP[offset]
# - ret (con caso especial para main)

class MIPSFun:
    def __init__(self, codegen):
        self.cg = codegen
        self.current_func = None
        self.pending_params = []  # params acumulados antes de call
        self.epilog_defined = {}   # func_label -> bool
        self.frame_effective = {}  # func_label -> frame_size usado

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
    def emit_prolog(self, func_label):
        self.current_func = func_label
        cg = self.cg

        f = cg.symtab.global_scope.resolve(func_label)
        declared_frame = getattr(f, "frame_size", 0) if f else 0
        local_need = cg.func_local_need.get(func_label, 0)
        frame_size = max(declared_frame, local_need)
        self.frame_effective[func_label] = frame_size

        cg.emit("    addi $sp, $sp, -8")
        cg.emit("    sw $fp, 4($sp)")
        cg.emit("    sw $ra, 0($sp)")
        cg.emit("    move $fp, $sp")

        # RESERVAR LOCALES primero (para que offsets FP[...] no cambien)
        if frame_size > 0:
            cg.emit(f"    addi $sp, $sp, -{frame_size}")

        # salvar registros callee-saved $s0-$s7 al final del frame
        cg.emit("    addi $sp, $sp, -32")
        for i in range(8):
            cg.emit(f"    sw $s{i}, {i*4}($sp)")


    def emit_epilog(self):
        """Epilog estándar."""
        cg = self.cg
        f = None
        if cg.symtab and cg.symtab.global_scope:
            f = cg.symtab.global_scope.resolve(self.current_func)
        frame_size = getattr(f, "frame_size", 0) if f else 0

        cg.emit("    # ---- EPILOG ----")
        # restaurar $s0-$s7 (están al final del frame)
        for i in range(8):
            cg.emit(f"    lw $s{i}, {i*4}($sp)")
        cg.emit("    addi $sp, $sp, 32")
        frame_size = self.frame_effective.get(self.current_func, frame_size)
        if frame_size and frame_size > 0:
            cg.emit(f"    addi $sp, $sp, {frame_size}")
        cg.emit("    lw $ra, 0($sp)")
        cg.emit("    lw $fp, 4($sp)")
        cg.emit("    addi $sp, $sp, 8")
        cg.emit("    beq $ra, $zero, __program_exit")
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
        self.pending_params.append(t_arg)

    def emit_call(self, func_label, argc, t_res):
        cg = self.cg
        # Si es método (Clase.metodo), setear 'this' desde el primer arg
        if isinstance(func_label, str) and "." in func_label and self.pending_params:
            this_temp = self.pending_params[0]
            reg_this = cg.tm.get_reg(this_temp)
            cg._load(this_temp, reg_this)
            cg.emit("    la $t9, this")
            cg.emit(f"    sw {reg_this}, 0($t9)")
            # si se conoce el tipo dinámico del objeto, usarlo para el label
            if hasattr(cg, "class_mod") and this_temp in cg.class_mod.obj_types:
                dyn_cls = cg.class_mod.obj_types[this_temp]
                cg.class_mod.global_obj_types["this"] = dyn_cls
                _, meth = func_label.split(".", 1)
                func_label = f"{dyn_cls}.{meth}"

        # aplicar mangle seguro si existe
        func_label = cg.func_label_map.get(func_label, func_label)

        cg.emit(f"    jal {func_label}")
        if argc and argc > 0:
            cg.emit(f"    addi $sp, $sp, {4 * argc}")
        reg_r = cg.tm.get_reg(t_res)
        cg.emit(f"    move {reg_r}, $v0")

        # invalidar meta vieja del temporal
        cg.temp_int.pop(t_res, None)
        cg.temp_string.pop(t_res, None)
        cg.temp_ptr[t_res] = reg_r
        cg.ptr_table[t_res] = reg_r
        self.pending_params.clear()


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
            # Primer ret: emitir epilog label inline; siguientes: saltar al mismo epilog
            if self.epilog_defined.get(self.current_func):
                cg.emit(f"    j {self.current_func}_epilog")
            else:
                self.epilog_defined[self.current_func] = True
                cg.emit(f"{self.current_func}_epilog:")
                self.emit_epilog()
