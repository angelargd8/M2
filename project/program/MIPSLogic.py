# ================================================================
# Manejo de expresiones lógicas en MIPS
# Implementa &&, || y ! sobre enteros (0 = false, !=0 = true)
# ================================================================

class MIPSLogic:
    def __init__(self, codegen):
        self.cg = codegen
        self.tm = codegen.tm

    def logical(self, op, a, b, r):
        """
        a && b, a || b
        Normalizamos a/b a 0/1 y aplicamos and/or.
        """
        reg_a = self.tm.get_reg(a)
        reg_b = self.tm.get_reg(b)
        reg_r = self.tm.get_reg(r)

        self.cg._load(a, reg_a)
        self.cg._load(b, reg_b)

        # normalización booleana
        self.cg.emit(f"    sne {reg_a}, {reg_a}, $zero")
        self.cg.emit(f"    sne {reg_b}, {reg_b}, $zero")

        if op == "&&":
            self.cg.emit(f"    and {reg_r}, {reg_a}, {reg_b}")
        elif op == "||":
            self.cg.emit(f"    or {reg_r}, {reg_a}, {reg_b}")
        else:
            raise Exception(f"MIPSLogic: operador lógico no soportado {op}")

        # limpiar metadatos de constantes
        self.cg.temp_int.pop(r, None)
        self.cg.temp_float.pop(r, None)
        self.cg.temp_ptr.pop(r, None)
        self.cg.temp_string.pop(r, None)

    def unary_not(self, a, r):
        """
        !a  =>  r = (a == 0 ? 1 : 0)
        """
        reg_a = self.tm.get_reg(a)
        reg_r = self.tm.get_reg(r)

        self.cg._load(a, reg_a)
        self.cg.emit(f"    seq {reg_r}, {reg_a}, $zero")

        self.cg.temp_int.pop(r, None)
        self.cg.temp_float.pop(r, None)
        self.cg.temp_ptr.pop(r, None)
        self.cg.temp_string.pop(r, None)
