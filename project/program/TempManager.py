# se usa el conteo de referencias

from TempPool import TempPool

class TempManager:
    def __init__(self):
        self.pool = TempPool()
        self.refcount={} # t -> numero de referencias pendientes
        self.label_count = 0 

        # Registros disponibles
        self.free_regs = [
            "$t0", "$t1", "$t2", "$t3", "$t4",
            "$t5", "$t6", "$t7", "$t8", "$t9", 
            "$t10", "$t11", "$t12", "$t13", "$t14",
            "$t15", "$t16", "$t17", "$t18", "$t19"
        ]

        # Mapa: temporal -> registro asignado
        self.temp_to_reg = {}

    def new_temp(self):
        t = self.pool.get()
        self.refcount[t] =0
        return t
    
    def add_ref(self, t):
        if t:
            self.refcount[t] = self.refcount.get(t, 0) + 1

    def release_ref(self, t):
        """
        Cuando el temp deja de usarse:
        - reducir refcount
        - si llega a cero: liberar temp y su registro físico
        """
        if not t or t not in self.refcount:
            return

        self.refcount[t] -= 1

        if self.refcount[t] <= 0:
            # Liberar registro MIPS
            if t in self.temp_to_reg:
                reg = self.temp_to_reg[t]
                self.free_regs.append(reg)
                del self.temp_to_reg[t]

            # Liberar temporal del TempPool
            self.pool.release(t)
            del self.refcount[t]

    def get_reg(self, temp):
        """
        Retorna un registro MIPS para el temporal.
        Si no tiene, asigna uno disponible.
        """
        if temp in self.temp_to_reg:
            return self.temp_to_reg[temp]

        if not self.free_regs:
            raise Exception("TempManager: no hay registros MIPS disponibles")

        reg = self.free_regs.pop(0)
        self.temp_to_reg[temp] = reg
        return reg

        
    def newLabel(self):
        #Genera una etiqueta única (L1, L2, L3, ...)
        self.label_count += 1
        return f"L{self.label_count}"
    