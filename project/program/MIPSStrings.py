# ================================================================
# Gestión de concatenación de strings:
# - Soporta strings literales (.data)
# - Soporta strings dinámicos (heap de syscall 9)
# - Soporta variables globales string (label: .word str_k)
# ================================================================

class MIPSStrings:
    def __init__(self, cg):
        self.cg = cg          # referencia al MIPSCodeGen
        self.tm = cg.tm       # TempManager
        self.counter = 0      # para generar etiquetas únicas por concatenación

    # -------------------------------------------------------------
    # Cargar puntero del string (literal, dinámico o global)
    # en el registro dst_reg (que ya viene de TempManager)
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

        # 3) variable global de tipo string: g_name: .word str_k
        if (
            isinstance(temp_name, str)
            and hasattr(cg.symtab, "global_scope")
            and temp_name in cg.symtab.global_scope.symbols
        ):
            sym = cg.symtab.global_scope.symbols[temp_name]
            if getattr(sym.type, "name", None) == "string":
                label = getattr(sym, "mips_label", temp_name)
                cg.emit(f"    la {dst_reg}, {label}")
                cg.emit(f"    lw {dst_reg}, 0({dst_reg})")
                return



        raise Exception(f"[MIPSStrings] '{temp_name}' no es string literal, dinámico ni global")

    # -------------------------------------------------------------
    # Concatena a + b → r
    # a y b deben representar strings (literal, global o heap)
    # -------------------------------------------------------------
    def concat_strings(self, a, b, r):
        cg = self.cg
        tm = self.tm
        self.counter += 1
        cid = self.counter

        # Pedimos registros a TempManager con nombres internos únicos
        avoid_args = {"$a0", "$a1", "$a2", "$a3"}
        reg_a   = tm._get_reg_internal(f"{r}_A", avoid=avoid_args)      # puntero a A
        reg_b   = tm._get_reg_internal(f"{r}_B", avoid=avoid_args)      # puntero a B
        reg_base = tm._get_reg_internal(f"{r}_BASE", avoid=avoid_args)  # base del nuevo buffer
        reg_cur  = tm._get_reg_internal(f"{r}_CUR", avoid=avoid_args)   # cursor dentro del buffer
        reg_chr  = tm._get_reg_internal(f"{r}_CHR", avoid=avoid_args)   # byte temporal

        # Cargar punteros de A y B
        self._load_str_ptr(a, reg_a)
        self._load_str_ptr(b, reg_b)

        # Reservar buffer (512 bytes, suficiente para tu ejemplo)
        cg.emit("    li $a0, 512")
        cg.emit("    li $v0, 9")
        cg.emit("    syscall")
        cg.emit(f"    move {reg_base}, $v0")
        cg.emit(f"    move {reg_cur}, {reg_base}")

        # Etiquetas únicas por temporal destino r
        label_copy_a = f"concat_copy_a_{r}_{cid}"
        label_copy_b = f"concat_copy_b_{r}_{cid}"
        label_done   = f"concat_done_{r}_{cid}"

        # Copiar A
        cg.emit(f"{label_copy_a}:")
        cg.emit(f"    lb {reg_chr}, 0({reg_a})")
        cg.emit(f"    sb {reg_chr}, 0({reg_cur})")
        cg.emit(f"    beq {reg_chr}, $zero, {label_copy_b}")
        cg.emit(f"    addi {reg_a}, {reg_a}, 1")
        cg.emit(f"    addi {reg_cur}, {reg_cur}, 1")
        cg.emit(f"    j {label_copy_a}")

        # Copiar B
        cg.emit(f"{label_copy_b}:")
        cg.emit(f"    lb {reg_chr}, 0({reg_b})")
        cg.emit(f"    sb {reg_chr}, 0({reg_cur})")
        cg.emit(f"    beq {reg_chr}, $zero, {label_done}")
        cg.emit(f"    addi {reg_b}, {reg_b}, 1")
        cg.emit(f"    addi {reg_cur}, {reg_cur}, 1")
        cg.emit(f"    j {label_copy_b}")

        cg.emit(f"{label_done}:")
        # terminador nulo
        cg.emit(f"    sb $zero, 0({reg_cur})")

        # Registrar puntero dinámico RESULTADO en r
        reg_r = tm.get_reg(r)                     # registro "oficial" para r
        cg.emit(f"    move {reg_r}, {reg_base}")  # r apunta al inicio del buffer

        cg.ptr_table[r] = reg_r
        cg.temp_ptr[r] = reg_r

        # limpiar metadata numérica / literal
        cg.temp_string.pop(r, None)
        cg.temp_int.pop(r, None)
        cg.temp_float.pop(r, None)

        # liberar registros auxiliares usados solo en esta concatenación
        tm.free_temp(f"{r}_A")
        tm.free_temp(f"{r}_B")
        tm.free_temp(f"{r}_BASE")
        tm.free_temp(f"{r}_CUR")
        tm.free_temp(f"{r}_CHR")
