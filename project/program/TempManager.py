# se usa el conteo de referencias

from TempPool import TempPool

class TempManager:
    def __init__(self):
        self.pool = TempPool()
        self.refcount={} # t -> numero de referencias pendientes
        self.label_count = 0 

    def new_temp(self):
        t = self.pool.get()
        self.refcount[t] =0
        return t
    
    def add_ref(self, t):
        if t:
            self.refcount[t] = self.refcount.get(t, 0) + 1

    def release_ref(self, t):
        if t: 
            self.refcount[t] -= 1
            if self.refcount[t] <= 0:
                self.pool.release(t)
                del self.refcount[t]
    
    def newLabel(self):
        #Genera una etiqueta única (L1, L2, L3, ...)
        self.label_count += 1
        return f"L{self.label_count}"
    