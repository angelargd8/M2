# ================================================================
# Manejo de try/catch en MIPS 
# ---------------------------------------------------------------
# Se asume un runtime de pila de handlers en memoria:
#   push_handler(label): guarda label en una pila global
#   pop_handler(): saca el último handler
#   get_exception(): entrega el valor de la excepción (o 0)
# ---------------------------------------------------------------
# Si no existe ese runtime, estas funciones son placeholders que
# permiten que el generador no falle; en SPIM puedes simularlo con
# una pila global simple.
# ================================================================

class MIPSTC:
    def __init__(self, codegen):
        self.cg = codegen
        self.tm = codegen.tm

    def push_handler(self, label):
        """
        push_handler label
        """
        self.cg.emit(f"    # push_handler {label}")
        self.cg.emit(f"    la $t9, exc_handler")
        self.cg.emit(f"    la $t8, {label}")
        self.cg.emit(f"    sw $t8, 0($t9)")

    def pop_handler(self):
        self.cg.emit("    # pop_handler")
        self.cg.emit("    la $t9, exc_handler")
        self.cg.emit("    sw $zero, 0($t9)")
        self.cg.emit("    la $t9, exc_value")
        self.cg.emit("    sw $zero, 0($t9)")

    def get_exception(self, t_dst):
        """
        get_exception -> t_dst
        """
        reg = self.tm.get_reg(t_dst)
        self.cg.emit("    # get_exception")
        self.cg.emit("    la $t9, exc_value")
        self.cg.emit(f"    lw {reg}, 0($t9)")
        # guardar copia en exc_tmp para impresiones posteriores
        self.cg.emit("    la $t8, exc_tmp")
        self.cg.emit(f"    sw {reg}, 0($t8)")
        # marcarlo como puntero (p. ej. str_div_zero)
        self.cg.ptr_table[t_dst] = reg
        self.cg.temp_ptr[t_dst] = reg
        self.cg.temp_int.pop(t_dst, None)
        self.cg.temp_string.pop(t_dst, None)
