# Manejo de STRINGS dinámicos en tiempo de ejecución.
# Implementa:  t_dest = t_left + t_right
# - calcula longitudes en runtime
# - usa sbrk para reservar memoria
# - copia byte por byte
# - guarda el puntero del resultado en ptr_table[t_dest]

class MIPSStrings:
    def __init__(self, cg):
        self.cg = cg  # referencia al MIPSCodeGen

    def concat_strings(self, t_left, t_right, t_dest):
        """
        Concatena strings dinámicos:
            t_dest = t_left + t_right

        El resultado es un puntero en memoria dinámica (heap).
        """

        left_label  = self.cg.temp_string.get(t_left)
        right_label = self.cg.temp_string.get(t_right)

        if left_label is None or right_label is None:
            raise Exception(f"Concatenación espera strings, recibió {t_left}, {t_right}")

        self.cg.emit("")
        self.cg.emit("    # ===== CONCAT START =====")

        # ================================================================
        # 1) Calcular longitud de left en runtime
        # ================================================================
        self.cg.emit(f"    la $t0, {left_label}")   # ptr left
        self.cg.emit("    move $t1, $zero")         # len_left = 0

        self.cg.emit("concat_left_len_loop:")
        self.cg.emit("    lb $t2, 0($t0)")
        self.cg.emit("    beq $t2, $zero, concat_left_len_done")
        self.cg.emit("    addi $t1, $t1, 1")
        self.cg.emit("    addi $t0, $t0, 1")
        self.cg.emit("    j concat_left_len_loop")

        self.cg.emit("concat_left_len_done:")

        # ================================================================
        # 2) Calcular longitud de right en runtime
        # ================================================================
        self.cg.emit(f"    la $t0, {right_label}")  # ptr right
        self.cg.emit("    move $t3, $zero")         # len_right = 0

        self.cg.emit("concat_right_len_loop:")
        self.cg.emit("    lb $t2, 0($t0)")
        self.cg.emit("    beq $t2, $zero, concat_right_len_done")
        self.cg.emit("    addi $t3, $t3, 1")
        self.cg.emit("    addi $t0, $t0, 1")
        self.cg.emit("    j concat_right_len_loop")

        self.cg.emit("concat_right_len_done:")

        # total_length = left + right + 1 (\0)
        self.cg.emit("    add $t4, $t1, $t3")
        self.cg.emit("    addi $t4, $t4, 1")

        # ================================================================
        # 3) Reservar memoria con sbrk
        # ================================================================
        self.cg.emit("    move $a0, $t4")
        self.cg.emit("    li $v0, 9         # syscall sbrk")
        self.cg.emit("    syscall")
        self.cg.emit("    move $t5, $v0     # t5 = new buffer")

        # Guardamos: t_dest → registro con puntero del buffer
        self.cg.ptr_table[t_dest] = "$t5"

        # ================================================================
        # 4) Copiar left al nuevo buffer
        # ================================================================
        self.cg.emit(f"    la $t0, {left_label}")   # ptr left
        self.cg.emit("    move $t6, $t5")           # ptr destino

        self.cg.emit("concat_copy_left:")
        self.cg.emit("    lb $t2, 0($t0)")
        self.cg.emit("    beq $t2, $zero, concat_left_done_copy")
        self.cg.emit("    sb $t2, 0($t6)")
        self.cg.emit("    addi $t6, $t6, 1")
        self.cg.emit("    addi $t0, $t0, 1")
        self.cg.emit("    j concat_copy_left")

        self.cg.emit("concat_left_done_copy:")

        # ================================================================
        # 5) Copiar right después de left
        # ================================================================
        self.cg.emit(f"    la $t0, {right_label}")

        self.cg.emit("concat_copy_right:")
        self.cg.emit("    lb $t2, 0($t0)")
        self.cg.emit("    beq $t2, $zero, concat_right_done_copy")
        self.cg.emit("    sb $t2, 0($t6)")
        self.cg.emit("    addi $t6, $t6, 1")
        self.cg.emit("    addi $t0, $t0, 1")
        self.cg.emit("    j concat_copy_right")

        self.cg.emit("concat_right_done_copy:")

        # ================================================================
        # 6) Null terminator
        # ================================================================
        self.cg.emit("    sb $zero, 0($t6)")

        # Registrar que t_dest es string dinámico
        self.cg.temp_ptr[t_dest] = True

        self.cg.emit("    # ===== CONCAT END =====")
        self.cg.emit("")
