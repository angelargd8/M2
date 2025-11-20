# ================================================================
#  Módulo de sentencias de control para MIPS
#  - Maneja: iftrue_goto, iffalse_goto, goto
#  - Se integra con TempManager y MIPSCodeGen
# ================================================================

class MIPSSen:
    def __init__(self, cg):
        self.cg = cg
        self.tm = cg.tm

    # ------------------------------------------------------------
    # iftrue_goto cond -> label
    # ------------------------------------------------------------
    def iftrue(self, cond, label):
        reg = self.tm.get_reg(cond)
        self.cg._load(cond, reg)

        # Si reg != 0 → saltar
        self.cg.emit(f"    bne {reg}, $zero, {label}")

    # ------------------------------------------------------------
    # iffalse_goto cond -> label
    # ------------------------------------------------------------
    def iffalse(self, cond, label):
        reg = self.tm.get_reg(cond)
        self.cg._load(cond, reg)

        # Si reg == 0 → saltar
        self.cg.emit(f"    beq {reg}, $zero, {label}")

    # ------------------------------------------------------------
    # goto label
    # ------------------------------------------------------------
    def goto(self, label):
        self.cg.emit(f"    j {label}")
