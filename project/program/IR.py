"""
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
    c: Optional[str] = None
    #ej: (add, t1, t2, t3) == t1 = t2 + t3

def make(op, a=None, b= None, c= None):
    return Instr(op, a, b, c)


def print_ir(ir):
    # simbolos
    OP_SYM = {
        'add': '+', 'sub': '-', 'mul': '*', 'div': '/', 'mod': '%',
        'eq': '==', 'ne': '!=', 'lt': '<', 'le': '<=', 'gt': '>', 'ge': '>=',
        'and': '&&', 'or': '||',
    }

    for ins in ir:
        op, a, b, c = ins.op, ins.a, ins.b, ins.c

        # Binarios con 3 direcciones: t = x OP y
        if op in OP_SYM:
            sym = OP_SYM[op]
            print(f"{a} = {b} {sym} {c}")
            continue

        # Asignación simple
        if op == 'copy':
            print(f"{a} = {b}")
            continue

        # Parámetros y llamadas
        if op == 'param':
            print(f"param {a}")
            continue

        if op == 'call':
            # si el destino es None o "_"  solo se muestra 'call ...'
            dst = (a or "").strip()
            if not dst or dst == "_":
                print(f"call {b}, nargs={c}")
            else:
                print(f"{dst} = call {b}, nargs={c}")
            continue

        # Retornos
        if op == 'ret':
            print(f"ret {a}")
            continue
        if op == 'ret_void':
            print("ret")
            continue

        # Control de flujo
        if op == 'label':
            print(f"{a}:")
            continue
        if op == 'goto':
            print(f"goto {a}")
            continue
        if op == 'if_goto':
            print(f"if {a} goto {b}")
            continue
        if op == 'iffalse_goto':
            print(f"if !{a} goto {b}")
            continue

        # Objetos / arreglos / listas
        if op == 'new':
            print(f"{a} = new {b}")
            continue
        if op == 'newlist':
            print(f"{a} = newlist {b}")
            continue
        if op == 'setidx':
            print(f"{a}[{b}] = {c}")
            continue
        if op == 'getidx':
            print(f"{a} = {b}[{c}]")
            continue
        if op == 'setprop':
            print(f"{a}.{b} = {c}")
            continue
        if op == 'getprop':
            print(f"{a} = {b}.{c}")
            continue
        if op == 'length':
            print(f"{a} = len({b})")
            continue

        # funciones
        if op == 'func':
            print(f"\nfunc {a}:")
            continue
        if op == 'endfunc':
            print(f"endfunc  # {a}\n")
            continue

        # clases
        if op == 'class':
            print(f"\nclass {a}:")
            continue
        if op == 'endclass':
            print(f"endclass  # {a}\n")
            continue
        
        # fallback
        print(f"{op} {a} {b} {c}".strip())