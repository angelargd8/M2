# pool de temporales para el reciclaje por lifetime de expresion
class TempPool:

    def __init__(self, prefix='t'):
        self.prefix = prefix
        self.free = []
        self.count = 0
        self.used= set()
        self.count =0 

    def get(self):
        if self.free:
            return self.free.pop()
        self.count += 1
        return f"t{self.count}"
    
    def release(self, t):
        if t and t.startswith('t'):
            self.free.append(t)
