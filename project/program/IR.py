"""
Representacion Intermedia
Modelo de codigo de tres direcciones

"""

from dataclasses import dataclass
from typing import Tuple, List, Optional, Union

Temp = str #variable temporal, t1, t2
Label = str # etiqueta l1, l2
Loc = str  #direccion

@dataclass
class Instr:
    op: str
    a: Optional[str] = None
    b: Optional[str] = None
    result: Optional[str] = None
    #ej: (add, t1, t2, t3) == t1 = t2 + t3

    @property
    def r(self):
        return self.result



def make(op, a=None, b= None, c= None):
    return Instr(op, a, b, c)




# convert to quads
# vamos a seguir la estructura como lo vimos en clase: op, arg1, arg2 y result
def to_quads(ir):
    #Convierte la representación del IR en lista de tuplas uniformes
    quads = []
    for ins in ir:
        if isinstance(ins, tuple):
            quads.append(ins)
        else:  # objeto Instr
            quads.append((ins.op, ins.a, ins.b, ins.r))
    return quads


def print_quads(quads, max_width=18):
    def s(x):
        return str(x)

    def crop(txt, w):
        txt = s(txt)
        return txt if len(txt) <= w else txt[: max(1, w - 1)] + "…"

    headers = ["operador", "arg1", "arg2", "result"]
    rows = [(op, x, y, r) for (op, x, y, r) in quads]

    # Ancho por columna
    widths = []
    for col in range(4):
        content_len = max([len(s(headers[col]))] + [len(s(row[col])) for row in rows]) if rows else len(headers[col])
        widths.append(min(content_len, max_width))

    def fmt_row(tup):
        return " | ".join(crop(tup[i], widths[i]).ljust(widths[i]) for i in range(4))

    sep = "-+-".join("-" * w for w in widths)

    # Print
    print(fmt_row(tuple(headers)))
    print(sep)
    for row in rows:
        print(fmt_row(row))