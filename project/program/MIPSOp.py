# ================================================================
#  Módulo de operaciones aritméticas y comparaciones para MIPS
# ================================================================

class MIPSOp:
    def __init__(self, gen):
        self.gen = gen
        self.tm = gen.tm

    # ============================================================
    # ARITMÉTICAS: int y float
    # ============================================================
    def arithmetic(self, op, a, b, r):
        """
        Maneja +, -, *, /, % sobre:
        - int / int  (registros enteros)
        - float / float (cuando tú generes esos casos)
        OJO: aquí NO se guardan constantes en temp_int / temp_float.
        """

        a_is_float = a in self.gen.temp_float
        b_is_float = b in self.gen.temp_float

        # --------------------------------------------------------
        # CASO 1: ambos son FLOAT (cuando vengan de copy float)
        # --------------------------------------------------------
        if a_is_float and b_is_float:
            fa = self.tm.get_freg(a)
            fb = self.tm.get_freg(b)
            fr = self.tm.get_freg(r)

            # Cargar literales float a sus fregs si es necesario
            self._ensure_float_loaded(a, fa)
            self._ensure_float_loaded(b, fb)

            if op == "+":
                self.gen.emit(f"    add.s {fr}, {fa}, {fb}")
            elif op == "-":
                self.gen.emit(f"    sub.s {fr}, {fa}, {fb}")
            elif op == "*":
                self.gen.emit(f"    mul.s {fr}, {fa}, {fb}")
            elif op == "/":
                self.gen.emit(f"    div.s {fr}, {fa}, {fb}")
            else:
                raise Exception("Operador float no soportado: " + op)

            # Resultado r es float dinámico → quitar meta de constante
            self._kill_meta(r)
            # MARCAMOS sólo que es float por tipo (sin valor constante)
            self.gen.temp_float[r] = None
            return

        # --------------------------------------------------------
        # CASO 2: ambos son ENTEROS
        # --------------------------------------------------------
        if (not a_is_float) and (not b_is_float):
            ra = self.tm.get_reg(a)
            rb = self.tm.get_reg(b)
            rr = self.tm.get_reg(r)

            self.gen._load(a, ra)
            self.gen._load(b, rb)

            if op == "+":
                self.gen.emit(f"    add {rr}, {ra}, {rb}")
            elif op == "-":
                self.gen.emit(f"    sub {rr}, {ra}, {rb}")
            elif op == "*":
                self.gen.emit(f"    mul {rr}, {ra}, {rb}")
            elif op in ("/", "%"):
                lbl_id = self.tm.newLabel()
                err_lbl = f"DZ_ERR_{lbl_id}"
                ok_lbl = f"DZ_OK_{lbl_id}"
                jmp_lbl = f"DZ_JMP_{lbl_id}"
                # check divisor zero
                self.gen.emit(f"    beq {rb}, $zero, {err_lbl}")
                self.gen.emit(f"    div {ra}, {rb}")
                if op == "/":
                    self.gen.emit(f"    mflo {rr}")
                else:
                    self.gen.emit(f"    mfhi {rr}")
                self.gen.emit(f"    j {ok_lbl}")
                # handler: set exc_value y saltar al handler
                self.gen.emit(f"{err_lbl}:")
                self.gen.emit("    la $t8, str_div_zero")
                self.gen.emit("    la $t9, exc_value")
                self.gen.emit("    sw $t8, 0($t9)")
                self.gen.emit("    la $t9, exc_handler")
                self.gen.emit("    lw $t9, 0($t9)")
                self.gen.emit(f"    beq $t9, $zero, {jmp_lbl}")
                self.gen.emit("    jr $t9")
                self.gen.emit(f"{jmp_lbl}:")
                # sin handler -> terminar
                self.gen.emit("    li $v0, 10")
                self.gen.emit("    syscall")
                self.gen.emit(f"{ok_lbl}:")
            else:
                raise Exception("Operador entero no soportado: " + op)

            # r es entero dinámico → NO guardar constante
            self._kill_meta(r)
            # (si quisieras marcar tipo int, podrías usar otro dict sólo de tipos)
            return

        # --------------------------------------------------------
        # CASO 3: mezcla int/float  → promover a float
        # --------------------------------------------------------
        # a int → float
        if not a_is_float:
            ra = self.tm.get_reg(a)
            fa = self.tm.get_freg(a)
            self.gen._load(a, ra)
            self.gen.emit(f"    mtc1 {ra}, {fa}")
            self.gen.emit(f"    cvt.s.w {fa}, {fa}")
            self.gen.temp_float[a] = None   # ahora lo tratamos como float
            a_is_float = True

        # b int → float
        if not b_is_float:
            rb = self.tm.get_reg(b)
            fb = self.tm.get_freg(b)
            self.gen._load(b, rb)
            self.gen.emit(f"    mtc1 {rb}, {fb}")
            self.gen.emit(f"    cvt.s.w {fb}, {fb}")
            self.gen.temp_float[b] = None
            b_is_float = True

        # ahora ambos son float → reutilizar lógica
        self.arithmetic(op, a, b, r)

    # ------------------------------------------------------------
    # helpers para floats
    # ------------------------------------------------------------
    def _ensure_float_loaded(self, t, freg):
        """
        Si t es un literal float (temp_float[t] = valor),
        genera li.s freg, valor. Si ya es dinámico (None),
        asumimos que freg ya tiene el valor correcto.
        """
        if t in self.gen.temp_float and self.gen.temp_float[t] is not None:
            val = self.gen.temp_float[t]
            self.gen.emit(f"    li.s {freg}, {val}")
            # ya no es constante en tiempo de ejecución
            self.gen.temp_float[t] = None

    def _kill_meta(self, t):
        """Borra info de constante / puntero / string del temporal t."""
        self.gen.temp_int.pop(t, None)
        self.gen.temp_float.pop(t, None)
        self.gen.temp_ptr.pop(t, None)
        self.gen.temp_string.pop(t, None)

    # ============================================================
    # COMPARACIONES: < <= > >= == !=   (int solamente por ahora)
    # ============================================================
    def comparison(self, op, a, b, r):
        reg_a = self.tm.get_reg(a)
        reg_b = self.tm.get_reg(b)
        reg_r = self.tm.get_reg(r)

        # cargar valores
        self.gen._load(a, reg_a)
        self.gen._load(b, reg_b)

        if op == "<":
            self.gen.emit(f"    slt {reg_r}, {reg_a}, {reg_b}")
        elif op == "<=":
            self.gen.emit(f"    sle {reg_r}, {reg_a}, {reg_b}")
        elif op == ">":
            self.gen.emit(f"    sgt {reg_r}, {reg_a}, {reg_b}")
        elif op == ">=":
            self.gen.emit(f"    sge {reg_r}, {reg_a}, {reg_b}")
        elif op == "==":
            self.gen.emit(f"    xor {reg_r}, {reg_a}, {reg_b}")
            self.gen.emit(f"    sltiu {reg_r}, {reg_r}, 1")
        elif op == "!=":
            self.gen.emit(f"    xor {reg_r}, {reg_a}, {reg_b}")
            self.gen.emit(f"    sltu {reg_r}, $zero, {reg_r}")
        else:
            raise Exception("Comparación no soportada: " + op)

        self._kill_meta(r)

    # ============================================================
    # LÓGICOS: &&  ||
    # ============================================================
    def logical(self, op, a, b, r):
        reg_a = self.tm.get_reg(a)
        reg_b = self.tm.get_reg(b)
        reg_r = self.tm.get_reg(r)

        self.gen._load(a, reg_a)
        self.gen._load(b, reg_b)

        # normalización booleana (0 o 1)
        self.gen.emit(f"    sne {reg_a}, {reg_a}, $zero")
        self.gen.emit(f"    sne {reg_b}, {reg_b}, $zero")

        if op == "&&":
            self.gen.emit(f"    and {reg_r}, {reg_a}, {reg_b}")
        elif op == "||":
            self.gen.emit(f"    or {reg_r}, {reg_a}, {reg_b}")
        else:
            raise Exception("Operador lógico no soportado: " + op)

        self._kill_meta(r)

    # ============================================================
    # NOT lógico
    # ============================================================
    def unary_not(self, a, r):
        reg_a = self.tm.get_reg(a)
        reg_r = self.tm.get_reg(r)

        self.gen._load(a, reg_a)
        self.gen.emit(f"    seq {reg_r}, {reg_a}, $zero")   # 1 si es cero, 0 si no

        self._kill_meta(r)
