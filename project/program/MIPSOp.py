# ================================================================
#  Módulo de operaciones aritméticas y comparaciones para MIPS
# ================================================================

class MIPSOp:
    def __init__(self, gen):
        self.gen = gen
        self.tm = gen.tm

    # ============================================================
    # ARITMÉTICAS: +  -  *  /  %
    # ============================================================
    def arithmetic(self, op, a, b, r):
        reg_a = self.tm.get_reg(a)
        reg_b = self.tm.get_reg(b)
        reg_r = self.tm.get_reg(r)

        self.gen._load(a, reg_a)
        self.gen._load(b, reg_b)

        if op == "+":
            self.gen.emit(f"    add {reg_r}, {reg_a}, {reg_b}")
        elif op == "-":
            self.gen.emit(f"    sub {reg_r}, {reg_a}, {reg_b}")
        elif op == "*":
            self.gen.emit(f"    mul {reg_r}, {reg_a}, {reg_b}")
        elif op == "/":
            self.gen.emit(f"    div {reg_a}, {reg_b}")
            self.gen.emit(f"    mflo {reg_r}")
        elif op == "%":
            self.gen.emit(f"    div {reg_a}, {reg_b}")
            self.gen.emit(f"    mfhi {reg_r}")
        else:
            raise Exception("Operación aritmética no soportada: " + op)

        # YA NO: self.gen.temp_int[r] = 0
        # solo limpia info de punteros/strings
        self.gen.temp_int.pop(r, None)
        self._kill_ptr(r)


    # ============================================================
    # COMPARACIONES: < <= > >= == !=
    # Resultado: 0 ó 1
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
            # set reg_r = (reg_a == reg_b)
            self.gen.emit(f"    xor {reg_r}, {reg_a}, {reg_b}")
            self.gen.emit(f"    sltiu {reg_r}, {reg_r}, 1")

        elif op == "!=":
            self.gen.emit(f"    xor {reg_r}, {reg_a}, {reg_b}")
            self.gen.emit(f"    sltu {reg_r}, $zero, {reg_r}")

        else:
            raise Exception("Comparación no soportada: " + op)

        self.gen.temp_int.pop(r, None)
        self._kill_ptr(r)


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

        self.gen.temp_int.pop(r, None)
        self._kill_ptr(r)


    # ============================================================
    # NOT lógico
    # ============================================================
    def unary_not(self, a, r):
        reg_a = self.tm.get_reg(a)
        reg_r = self.tm.get_reg(r)

        self.gen._load(a, reg_a)
        self.gen.emit(f"    seq {reg_r}, {reg_a}, $zero")   # 1 si es cero, 0 si no

        self.gen.temp_int.pop(r, None)
        self._kill_ptr(r)


    # ============================================================
    # Limpia estados de string/puntero
    # ============================================================
    def _kill_ptr(self, t):
        self.gen.temp_ptr.pop(t, None)
        self.gen.temp_string.pop(t, None)
        self.gen.ptr_table.pop(t, None)
