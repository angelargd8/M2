# ================================================================
# Gestión de concatenación de strings:
# - Soporta strings literales (.data)
# - Soporta strings dinámicos (heap de syscall 9)
# - Soporta variables globales string (label: .word str_k)
# ================================================================

class MIPSStrings:
    def __init__(self, cg):
        self.cg = cg  # referencia al MIPSCodeGen

    # -------------------------------------------------------------
    # Cargar puntero del string (literal, dinámico o global)
    # -------------------------------------------------------------
    def _load_str_ptr(self, temp_name, dst_reg):
        cg = self.cg

        # 1) string literal (temp -> label str_k en .data)
        if temp_name in cg.temp_string:
            label = cg.temp_string[temp_name]
            cg.emit(f"    la {dst_reg}, {label}")
            return

        # 2) string dinámico (temp -> registro en ptr_table)
        if temp_name in cg.ptr_table:
            reg_ptr = cg.ptr_table[temp_name]   # "$tX"
            cg.emit(f"    move {dst_reg}, {reg_ptr}")
            return

        # 3) variable global de tipo string: addFive: .word str_k
        if (
            isinstance(temp_name, str)
            and hasattr(cg.symtab, "global_scope")
            and temp_name in cg.symtab.global_scope.symbols
        ):
            sym = cg.symtab.global_scope.symbols[temp_name]
            # Asumimos que el type tiene atributo name == "string"
            if getattr(sym.type, "name", None) == "string":
                # dst_reg = *addFive (cargar puntero al literal)
                cg.emit(f"    la {dst_reg}, {temp_name}")
                cg.emit(f"    lw {dst_reg}, 0({dst_reg})")
                return

        # Si llega aquí, no sabemos qué es
        raise Exception(f"[MIPSStrings] '{temp_name}' no es string literal, dinámico ni global")

    # -------------------------------------------------------------
    # Concatena t_left + t_right → t_dest
    # t_left y t_right deben representar strings (literal, global o heap)
    # -------------------------------------------------------------
    def concat_strings(self, t_left, t_right, t_dest):
        cg = self.cg
        tm = cg.tm

        cg.emit("")
        cg.emit("    # ===== CONCAT START =====")

        # ---------------------------------------------------------
        # 1) LEN LEFT
        # ---------------------------------------------------------
        self._load_str_ptr(t_left, "$t0")
        L_l_loop = tm.newLabel()
        L_l_done = tm.newLabel()

        cg.emit("    move $t2, $zero  # len_left")
        cg.emit(f"{L_l_loop}:")
        cg.emit("    lb $t3, 0($t0)")
        cg.emit(f"    beq $t3, $zero, {L_l_done}")
        cg.emit("    addi $t2, $t2, 1")
        cg.emit("    addi $t0, $t0, 1")
        cg.emit(f"    j {L_l_loop}")
        cg.emit(f"{L_l_done}:")

        # ---------------------------------------------------------
        # 2) LEN RIGHT
        # ---------------------------------------------------------
        self._load_str_ptr(t_right, "$t0")
        L_r_loop = tm.newLabel()
        L_r_done = tm.newLabel()

        cg.emit("    move $t4, $zero  # len_right")
        cg.emit(f"{L_r_loop}:")
        cg.emit("    lb $t3, 0($t0)")
        cg.emit(f"    beq $t3, $zero, {L_r_done}")
        cg.emit("    addi $t4, $t4, 1")
        cg.emit("    addi $t0, $t0, 1")
        cg.emit(f"    j {L_r_loop}")
        cg.emit(f"{L_r_done}:")

        # ---------------------------------------------------------
        # 3) RESERVAR MEMORIA
        # ---------------------------------------------------------
        cg.emit("    add $t5, $t2, $t4")
        cg.emit("    addi $t5, $t5, 1")  # + '\0'
        cg.emit("    move $a0, $t5")
        cg.emit("    li $v0, 9")
        cg.emit("    syscall")
        cg.emit("    move $t6, $v0")     # buffer nuevo

        # registrar puntero dinámico
        cg.ptr_table[t_dest] = "$t6"
        cg.temp_ptr[t_dest] = "$t6"
        cg.temp_string.pop(t_dest, None)

        # ---------------------------------------------------------
        # 4) COPIAR LEFT
        # ---------------------------------------------------------
        self._load_str_ptr(t_left, "$t0")
        L_cl_loop = tm.newLabel()
        L_cl_done = tm.newLabel()

        cg.emit("    move $t7, $t6  # write cursor")
        cg.emit(f"{L_cl_loop}:")
        cg.emit("    lb $t3, 0($t0)")
        cg.emit(f"    beq $t3, $zero, {L_cl_done}")
        cg.emit("    sb $t3, 0($t7)")
        cg.emit("    addi $t7, $t7, 1")
        cg.emit("    addi $t0, $t0, 1")
        cg.emit(f"    j {L_cl_loop}")
        cg.emit(f"{L_cl_done}:")

        # ---------------------------------------------------------
        # 5) COPIAR RIGHT
        # ---------------------------------------------------------
        self._load_str_ptr(t_right, "$t0")
        L_cr_loop = tm.newLabel()
        L_cr_done = tm.newLabel()

        cg.emit(f"{L_cr_loop}:")
        cg.emit("    lb $t3, 0($t0)")
        cg.emit(f"    beq $t3, $zero, {L_cr_done}")
        cg.emit("    sb $t3, 0($t7)")
        cg.emit("    addi $t7, $t7, 1")
        cg.emit("    addi $t0, $t0, 1")
        cg.emit(f"    j {L_cr_loop}")
        cg.emit(f"{L_cr_done}:")

        # ---------------------------------------------------------
        # 6) NULL TERMINATOR
        # ---------------------------------------------------------
        cg.emit("    sb $zero, 0($t7)")
        cg.emit("    # ===== CONCAT END =====")
        cg.emit("")
