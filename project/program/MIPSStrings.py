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
    def concat_strings(self, a, b, r):
        # Obtener puntero de A
        reg_a = self.cg.tm.get_reg(a)
        if a in self.cg.temp_string:
            label = self.cg.temp_string[a]
            self.cg.emit(f"    la {reg_a}, {label}")
        elif a in self.cg.ptr_table:
            self.cg.emit(f"    move {reg_a}, {self.cg.ptr_table[a]}")
        else:
            raise Exception(f"concat: A no es string: {a}")

        # Obtener puntero de B
        reg_b = self.cg.tm.get_reg(b)
        if b in self.cg.temp_string:
            label = self.cg.temp_string[b]
            self.cg.emit(f"    la {reg_b}, {label}")
        elif b in self.cg.ptr_table:
            self.cg.emit(f"    move {reg_b}, {self.cg.ptr_table[b]}")
        else:
            raise Exception(f"concat: B no es string: {b}")

        # Reservar buffer
        reg_r = self.cg.tm.get_reg(r)
        self.cg.emit("    li $a0, 512")
        self.cg.emit("    li $v0, 9")
        self.cg.emit("    syscall")
        self.cg.emit(f"    move {reg_r}, $v0")

        # Punteros de recorrido
        self.cg.emit(f"    move $t4, {reg_r}")  # cursor destino
        self.cg.emit(f"    move $t5, {reg_a}")  # cursor en A
        self.cg.emit(f"    move $t6, {reg_b}")  # cursor en B

        # Copiar A
        self.cg.emit(f"concat_copy_a_{r}:")
        self.cg.emit("    lb $t0, 0($t5)")
        self.cg.emit("    sb $t0, 0($t4)")
        self.cg.emit(f"    beq $t0, $zero, concat_copy_b_{r}")
        self.cg.emit("    addi $t5, $t5, 1")
        self.cg.emit("    addi $t4, $t4, 1")
        self.cg.emit(f"    j concat_copy_a_{r}")

        # Copiar B
        self.cg.emit(f"concat_copy_b_{r}:")
        self.cg.emit("    lb $t0, 0($t6)")
        self.cg.emit("    sb $t0, 0($t4)")
        self.cg.emit(f"    beq $t0, $zero, concat_done_{r}")
        self.cg.emit("    addi $t6, $t6, 1")
        self.cg.emit("    addi $t4, $t4, 1")
        self.cg.emit(f"    j concat_copy_b_{r}")

        self.cg.emit(f"concat_done_{r}:")

        # Registrar puntero dinámico
        self.cg.ptr_table[r] = reg_r
        self.cg.temp_ptr[r] = reg_r
        if r in self.cg.temp_string:
            del self.cg.temp_string[r]

        

