# se usa el conteo de referencias

from TempPool import TempPool

class TempManager:
    def __init__(self, codegen=None):
        self.pool = TempPool()
        self.refcount={} # t -> numero de referencias pendientes
        self.label_count = 0 
        self.temp_to_freg = {}
        self.pinned = set()    # temporales que no deben liberarse
        self._base_free_regs = [
            "$t0", "$t1", "$t2", "$t3", "$t4",
            "$t5", "$t6", "$t7", "$t8", "$t9",
            "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
            "$a0", "$a1", "$a2", "$a3",
        ]
        self.codegen = codegen

        # Registros disponibles
        self.free_regs = list(self._base_free_regs)

        self.free_fregs = [
            "$f0", "$f1", "$f2", "$f3", "$f4", "$f5",
            "$f6", "$f7", "$f8", "$f9", "$f10", "$f11",
            "$f12", "$f13", "$f14", "$f15",
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

        # temporales "anclados" (por ejemplo, variables de bloque en main) no se liberan
        if t in self.pinned:
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

    def pin(self, temp):
        """Marca un temporal como persistente (no se libera automáticamente)."""
        self.pinned.add(temp)

    def free_temp(self, temp):
        """Libera explícitamente el registro asociado a un temporal."""
        if temp in self.temp_to_reg:
            reg = self.temp_to_reg[temp]
            self.free_regs.append(reg)
            del self.temp_to_reg[temp]
        self.refcount.pop(temp, None)
        self.pinned.discard(temp)

    def get_reg(self, temp):
        return self._get_reg_internal(temp, avoid=None)

    def _get_reg_internal(self, temp, avoid):
        """
        Retorna un registro MIPS para el temporal.
        Si no tiene, asigna uno disponible.
        """
        if temp in self.temp_to_reg:
            return self.temp_to_reg[temp]

        # Si es un temporal "pinneado", preferir registros $s (callee-saved)
        if temp in self.pinned:
            for i, reg in enumerate(self.free_regs):
                if reg.startswith("$s"):
                    if avoid and reg in avoid:
                        continue
                    self.free_regs.pop(i)
                    self.temp_to_reg[temp] = reg
                    return reg

        # elegir el primer registro que no esté en avoid
        if avoid:
            for i, reg in enumerate(self.free_regs):
                if reg in avoid:
                    continue
                self.free_regs.pop(i)
                self.temp_to_reg[temp] = reg
                return reg

        if not self.free_regs:
            detalles = []
            for k in sorted(self.temp_to_reg.keys()):
                rc = self.refcount.get(k, None)
                if rc is None:
                    detalles.append(f"{k}(rc=?)")
                else:
                    detalles.append(f"{k}(rc={rc})")
            ocupados = ", ".join(detalles)
            raise Exception(f"TempManager: no hay registros MIPS disponibles (ocupados: {ocupados})")

        reg = self.free_regs.pop(0)
        self.temp_to_reg[temp] = reg
        return reg
    
    
    def get_freg(self, temp):
        if temp in self.temp_to_freg:
            return self.temp_to_freg[temp]

        if not self.free_fregs:
            raise Exception("TempManager: no hay registros flotantes disponibles")

        reg = self.free_fregs.pop(0)
        self.temp_to_freg[temp] = reg
        return reg
            
    def newLabel(self):
        #Genera una etiqueta única (L1, L2, L3, ...)
        self.label_count += 1
        return f"L{self.label_count}"

    def reset_regs(self):
        """Reinicia asignaciones de registros (útil al entrar a una función)."""
        self.free_regs = list(self._base_free_regs)
        self.temp_to_reg.clear()
        self.temp_to_freg.clear()
