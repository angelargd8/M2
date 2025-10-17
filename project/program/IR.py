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


def print_ir(ir, symtab=None):
    # simbolos
    OP_SYM = {
        'add': '+', 'sub': '-', 'mul': '*', 'div': '/', 'mod': '%',
        'eq': '==', 'ne': '!=', 'lt': '<', 'le': '<=', 'gt': '>', 'ge': '>=',
        'and': '&&', 'or': '||',
    }

    def _is_int(x: str) -> bool:
        try:
            int(str(x))
            return True
        except Exception:
            return False

    def _fmt_addr(base: Optional[str], off: Optional[str]) -> str:
        b = "" if base is None else str(base)
        o = "" if off  is None else str(off)
        if not b and not o: return "[]"
        if b and not o:     return f"{b}"
        if not b and o:     return f"{o}"
        if b == "GP" and not _is_int(o):
            return f"{o}"
        return f"{b}+{o}".replace("+-", "-")

    # -------- estado contextual para anotaciones --------
    current_func_name = None
    current_func_sym  = None
    current_class_name = None
    rev_params: dict[int,str] = {}
    rev_locals: dict[int,str] = {}
    rev_fields: dict[int,str] = {}   # offset -> fieldName (solo clase actual)
    temps_from_this: set[str] = set()  # temps que provienen de 'this'

    def _reset_rev_maps():
        nonlocal rev_params, rev_locals, rev_fields, temps_from_this
        rev_params, rev_locals, rev_fields = {}, {}, {}
        temps_from_this = set()

    def _lookup_func_symbol(fname: str):
        if symtab is None:
            return None
        f = symtab.global_scope.resolve(fname)
        if f is None:
            f = symtab.global_scope.resolve(fname.split('.')[-1])  # fallback
        return f

    def _build_rev_maps(fsym):
        _reset_rev_maps()
        if not fsym:
            return
        # params (offsets positivos)
        for name, off in (getattr(fsym, 'param_offsets', {}) or {}).items():
            try:
                rev_params[int(off)] = name
            except Exception:
                pass
        # locals (offsets negativos)
        for name, off in (getattr(fsym, 'local_offsets', {}) or {}).items():
            try:
                rev_locals[int(off)] = name
            except Exception:
                pass

    def _build_field_rev_map_for_class(cname: Optional[str]):
        nonlocal rev_fields
        rev_fields = {}
        if not symtab or not cname:
            return
        T = symtab.types.get(cname)
        if not T:
            return
        offmap = getattr(T, "_field_offsets", {}) or {}
        for fname, off in offmap.items():
            try:
                rev_fields[int(off)] = fname
            except Exception:
                pass

    def _comment_for_addr(base, off) -> str:
        # Anotación para variables (FP +/-)
        if base == "FP" and _is_int(off):
            ioff = int(off)
            if ioff >= 0 and ioff in rev_params:
                return f" ; {rev_params[ioff]}"
            if ioff < 0 and ioff in rev_locals:
                return f" ; {rev_locals[ioff]}"
        # Anotación para globals (GP + etiqueta)
        if base == "GP" and off and not _is_int(off):
            return f" ; {off}"
        # Anotación para this-campos cuando base es temp from 'this'
        if base in temps_from_this and _is_int(off) and rev_fields:
            ioff = int(off)
            if ioff in rev_fields:
                return f" ; this.{rev_fields[ioff]}"
        return ""

    def _comment_for_prop(obj_base, field_name: str) -> str:
        # Si es 'this', intenta anexar también el offset: ; this.x @+OFF
        if obj_base == "this" and rev_fields:
            # busca offset por nombre
            for off, fname in rev_fields.items():
                if fname == field_name:
                    return f" ; this.{field_name} @+{off}"
            return f" ; this.{field_name}"
        # Si el objeto es un temp que proviene de this
        if obj_base in temps_from_this and rev_fields:
            for off, fname in rev_fields.items():
                if fname == field_name:
                    return f" ; this.{field_name} @+{off}"
            return f" ; this.{field_name}"
        # Fallback: solo el nombre del campo
        return f" ; .{field_name}"
    
    # imprimir
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
            # rastrea temps que vienen de 'this'
            if str(b) == "this":
                temps_from_this.add(str(a))
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
            cm = _comment_for_prop(a, b)   # objeto=a, campo=b
            print(f"{a}.{b} = {c}{cm}")
            continue
        if op == 'getprop':
            cm = _comment_for_prop(b, c)   # objeto=b, campo=c
            print(f"{a} = {b}.{c}{cm}")
            continue
        if op == 'length':
            print(f"{a} = len({b})")
            continue

        # funciones
        if op == 'func':
            current_func_name = a
            current_func_sym  = _lookup_func_symbol(current_func_name)
            # clase actual, si el nombre es Clase.metodo
            current_class_name = a.split('.')[0] if '.' in str(a) else None
            _build_rev_maps(current_func_sym)
            _build_field_rev_map_for_class(current_class_name)
            temps_from_this = set()
            print(f"\nfunc {a}:")
            continue

        if op == 'endfunc':
            print(f"endfunc  # {a}\n")
            current_func_name = None
            current_func_sym  = None
            current_class_name = None
            _reset_rev_maps()
            continue
    
        # clases
        if op == 'class':
            print(f"\nclass {a}:")
            continue
        if op == 'endclass':
            print(f"endclass  # {a}\n")
            continue

        # memoria
        if op == 'enter':
            print(f"enter {a}")
            continue
        if op == 'leave':
            print("leave")
            continue
        if op == 'load':
            addr = _fmt_addr(b, c)
            cmnt = _comment_for_addr(b, c)
            print(f"{a} = MEM[{addr}]{cmnt}")
            continue
        if op == 'store':
            addr = _fmt_addr(a, b)
            cmnt = _comment_for_addr(a, b)
            print(f"MEM[{addr}] = {c}{cmnt}")
            continue
        
        # default: imprimir todo
        print(f"{op} {a} {b} {c}".strip())
        

def print_ir_modern(ir):
    """
    Imprime un IR plano y legible, diseñado para el flujo de IRGenerator.
    Ejemplo de salida:
        t1 = a
        t2 = b
        t3 = t1 + t2
        t = t3
        print t
    """
    if not ir:
        print("(IR vacío)")
        return

    OP_MAP = {
        '+': '+', '-': '-', '*': '*', '/': '/',
        '%': '%', '==': '==', '!=': '!=',
        '<': '<', '<=': '<=', '>': '>', '>=': '>=',
    }

    for ins in ir:
        # soporta tuplas o Instr
        op = ins.op if hasattr(ins, "op") else ins[0]
        a  = ins.a  if hasattr(ins, "a") else ins[1]
        b  = ins.b  if hasattr(ins, "b") else ins[2]
        c  = ins.c  if hasattr(ins, "c") else ins[3]

        # limpia valores None
        def fmt(x):
            return "" if x is None else str(x)

        op, a, b, c = fmt(op), fmt(a), fmt(b), fmt(c)

        # === formato según tipo de operación ===

        # operadores binarios
        if op in ['+', '-', '*', '/', '%']:
            print(f"{c} = {a} {op} {b}")
            continue

        # copy literal o variable
        if op == 'copy':
            print(f"{c} = {a}")
            continue

        # load variable
        if op == 'load':
            print(f"{c} = {a}")
            continue

        # store variable
        if op == 'store':
            print(f"{c} = {a}")
            continue

        # print statement
        if op == 'print':
            print(f"print {a}")
            continue

        # labels y saltos
        if op == 'label':
            print(f"{a}:")
            continue
        if op == 'goto':
            print(f"goto {c}")
            continue
        if op == 'if_true':
            print(f"if {a} goto {c}")
            continue
        if op == 'if_false':
            print(f"if !{a} goto {c}")
            continue

        # llamada a función
        if op == 'param':
            print(f"param {a}")
            continue
        if op == 'call':
            nargs = b or "?"
            if c:
                print(f"{c} = call {a}, nargs={nargs}")
            else:
                print(f"call {a}, nargs={nargs}")
            continue

        # default
        print(f"{op} {a} {b} {c}".strip())



# convert to quads
# vamos a seguir la estructura como lo vimos en clase: op, arg1, arg2 y result
def to_quads(ir):
    #Convierte la representación del IR en lista de tuplas uniformes
    quads = []
    for ins in ir:
        if isinstance(ins, tuple):
            quads.append(ins)
        else:  # objeto Instr
            quads.append((ins.op, ins.a, ins.b, ins.c))
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