# Concatenación de strings en tiempo de ejecución usando MIPS:
#   - obtiene direcciones de t_left y t_right
#   - calcula longitudes
#   - usa sbrk para reservar memoria
#   - copia ambas cadenas
#   - retorna pointer en un temporal

class MIPSStrings:
    def __init__(self, cg):
        self.cg = cg

    def concat_strings(self, t_left, t_right, t_dest):
        """
        Crea código MIPS para concatenar strings dinámicamente:
            t_dest = t_left + t_right
        """

        # =============================
        # 1. Obtener labels desde MIPSCodeGen
        # =============================
        left_label  = self.cg.temp_string.get(t_left)
        right_label = self.cg.temp_string.get(t_right)

        if left_label is None or right_label is None:
            raise Exception("Concatenación requiere dos temporales string.")

        # ================================================================
        # ETAPA 1: Calcular longitudes en tiempo de ejecución
        # ================================================================
        self.cg.emit("")
        self.cg.emit("    # ===== CONCAT START =====")

        # Calculamos len(left)
        self.cg.emit(f"    la $t0, {left_label}")     # ptr left
        self.cg.emit("    move $t1, $zero")           # len_left = 0

        self.cg.emit("concat_left_len_loop:")
        self.cg.emit("    lb $t2, 0($t0)")
        self.cg.emit("    beq $t2, $zero, concat_left_len_done")
        self.cg.emit("    addi $t1, $t1, 1")
        self.cg.emit("    addi $t0, $t0, 1")
        self.cg.emit("    j concat_left_len_loop")

        self.cg.emit("concat_left_len_done:")
        # $t1 = len_left

        # Calculamos len(right)
        self.cg.emit(f"    la $t0, {right_label}")    # ptr right
        self.cg.emit("    move $t3, $zero")           # len_right = 0

        self.cg.emit("concat_right_len_loop:")
        self.cg.emit("    lb $t2, 0($t0)")
        self.cg.emit("    beq $t2, $zero, concat_right_len_done")
        self.cg.emit("    addi $t3, $t3, 1")
        self.cg.emit("    addi $t0, $t0, 1")
        self.cg.emit("    j concat_right_len_loop")

        self.cg.emit("concat_right_len_done:")
        # $t3 = len_right

        # total_length = left + right + 1
        self.cg.emit("    add $t4, $t1, $t3")
        self.cg.emit("    addi $t4, $t4, 1")   # NUL terminator

        # ================================================================
        # ETAPA 2: Reservar memoria con sbrk
        # ================================================================
        self.cg.emit("    move $a0, $t4")
        self.cg.emit("    li $v0, 9      # sbrk syscall")
        self.cg.emit("    syscall")
        self.cg.emit("    move $t5, $v0  # t5 = new buffer")

        # Guardar la dirección como string temporal
        self.cg.temp_string[t_dest] = f"ptr_{t_dest}"

        # No existe un label real en .data, así que we keep runtime pointer
        # Save pointer mapping for load/print
        self.cg.runtime_ptrs[t_dest] = True

        # ================================================================
        # ETAPA 3: Copiar string2 y string2 a buffer
        # ================================================================
        # copy left → t5
        self.cg.emit(f"    la $t0, {left_label}")
        self.cg.emit("    move $t6, $t5")

        self.cg.emit("concat_copy_left:")
        self.cg.emit("    lb $t2, 0($t0)")
        self.cg.emit("    beq $t2, $zero, concat_left_done_copy")
        self.cg.emit("    sb $t2, 0($t6)")
        self.cg.emit("    addi $t6, $t6, 1")
        self.cg.emit("    addi $t0, $t0, 1")
        self.cg.emit("    j concat_copy_left")

        self.cg.emit("concat_left_done_copy:")

        # copy right → after left
        self.cg.emit(f"    la $t0, {right_label}")

        self.cg.emit("concat_copy_right:")
        self.cg.emit("    lb $t2, 0($t0)")
        self.cg.emit("    beq $t2, $zero, concat_right_done_copy")
        self.cg.emit("    sb $t2, 0($t6)")
        self.cg.emit("    addi $t6, $t6, 1")
        self.cg.emit("    addi $t0, $t0, 1")
        self.cg.emit("    j concat_copy_right")

        self.cg.emit("concat_right_done_copy:")

        # null terminator
        self.cg.emit("    sb $zero, 0($t6)")

        # ================================================================
        # Guardar buffer pointer en $v0 para uso por print
        # ================================================================
        self.cg.temp_ptr[t_dest] = True
        self.cg.emit(f"    move $v1, $t5     # result pointer for t_dest={t_dest}")

        self.cg.emit("    # ===== CONCAT END =====")
        self.cg.emit("")
