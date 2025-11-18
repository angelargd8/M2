"""
Traductor del codigo de tres direcciones a MIPS
"""

from typing import List, Dict, Any

"""
asignador de registros temporales MIPS
mapea nombres de temporales/variables a $t0-$t9

si se queda sin registros, los reutiliza
"""
class RegAllocator:
    def __init__(self):
        self.free = ["$t0","$t1","$t2","$t3","$t4","$t5","$t6","$t7","$t8","$t9"]
        self.map = {}

    def get(self, name):
        if name in self.map:
            return self.map[name]
        if self.free:
            r = self.free.pop(0)
            self.map[name] = r
            return r

        k = next(iter(self.map))
        self.map[name] = self.map[k]
        del self.map[k]
        return self.map[name]
    


class MIPSCodeGen:
    def __init__(self, quads, symtab=None):
        self.quads = quads
        self.symtab = symtab
        self.lines = []
        self.regs = RegAllocator()
        self.offsets = {}
        self.next_off = -4

    def emit(self, s=""):
        self.lines.append(s)

    # Frame offset for normal variables
    def offset(self, name):
        if name not in self.offsets:
            self.offsets[name] = self.next_off
            self.next_off -= 4
        return f"{self.offsets[name]}($fp)"

    # FP[13] → -13($fp)
    def is_fp_index(self, x):
        return isinstance(x,str) and x.startswith("FP[") and x.endswith("]")

    def fp_offset(self, x):
        n = int(x[3:-1])
        return f"-{n}($fp)"

    # Const?
    def is_const(self, x):
        if x is None: return False
        if isinstance(x,(int,float)): return True
        if isinstance(x,str) and x.isdigit(): return True
        if isinstance(x,str) and x.startswith('-') and x[1:].isdigit(): return True
        return False

    # Carga operand en registro
    def load(self, val, reg):
        if self.is_const(val):
            self.emit(f"    li {reg}, {val}")
        elif self.is_fp_index(val):
            self.emit(f"    lw {reg}, {self.fp_offset(val)}")
        elif isinstance(val,str):
            self.emit(f"    lw {reg}, {self.offset(val)}")
        else:
            self.emit(f"    # [ERROR] load desconocido {val}")

    # Guarda registro en destino
    def save(self, reg, dest):
        if self.is_fp_index(dest):
            self.emit(f"    sw {reg}, {self.fp_offset(dest)}")
        else:
            self.emit(f"    sw {reg}, {self.offset(dest)}")

    # -------------------------------------------
    #  MAIN ENTRY
    # -------------------------------------------
    def generate(self):
        # self.emit(".data\n")
        self.emit(".text")
        self.emit(".globl main\n")
        self.emit("main:")
        self.emit("    move $fp, $sp\n")

        for q in self.quads:
            self.translate(q)

        # main exit
        self.emit("    li $v0, 10")
        self.emit("    syscall")
        return "\n".join(self.lines)

    # -------------------------------------------
    #  TRADUCTOR PRINCIPAL
    # -------------------------------------------
    def translate(self, quad):
        op,a,b,r = quad

        # COPY
        if op == "copy":
            self.gen_copy(a,r)

        # LOAD/STORE
        elif op == "load":
            self.gen_load(a,r)
        elif op == "store":
            self.gen_store(a,r)

        # Arithmetic
        elif op in ["+","-","*"]:
            self.gen_arith(op,a,b,r)

        # Comparisons → produce boolean (0/1)
        elif op in ["<",">","<=",">=","==","!="]:
            self.gen_compare(op,a,b,r)

        # Branches
        elif op == "iftrue_goto":
            self.gen_iftrue(a,r)
        elif op == "iffalse_goto":
            self.gen_iffalse(a,r)
        elif op == "if_goto":
            self.gen_iftrue(a,r)
        elif op == "goto":
            self.emit(f"    j {r}")

        elif op == "label":
            self.emit(f"{a}:") if a else self.emit(f"{r}:")

        # Function flow
        elif op == "call":
            self.gen_call(a)
        elif op == "move_ret":
            self.gen_move_ret(r)
        elif op == "ret":
            self.gen_ret(a)
        elif op == "enter":
            self.gen_enter(a)
        elif op == "leave":
            self.emit("    move $sp, $fp")
        elif op == "push":
            self.gen_push(a)
        elif op == "pop":
            self.gen_pop(a)

        # Print
        elif op == "print":
            self.gen_print(a)

        elif op == "length":
            self.gen_length(a, r)

        elif op == "getidx":
            self.gen_getidx(a, b, r)

        elif op == "alloc":
            self.gen_alloc(a, r)

        elif op == "getprop":
            self.gen_getprop(a, b, r)

        elif op == "try_begin":
            self.gen_try_begin(r)   # r = label del handler

        elif op == "try_end":
            self.gen_try_end()

        elif op == "catch_begin":
            # a = nombre de la variable de error, r = label de salida del catch
            self.gen_catch_begin(a, r)

        elif op == "catch_end":
            self.gen_catch_end(r)   # r = label a donde saltar después del catch

        else:
            self.emit(f"    # [UNIMPLEMENTED] {quad}")

    # -------------------------------------------
    # IMPLEMENTACIONES
    # -------------------------------------------

    def gen_copy(self, src, dest):
        reg = self.regs.get(dest)
        self.load(src,reg)
        self.save(reg,dest)

    def gen_load(self, src, dest):
        reg = self.regs.get(dest)
        self.load(src,reg)
        self.save(reg,dest)

    def gen_store(self, src, dest):
        if src is None:
            self.emit(f"    # store None → {dest}")
            return
        reg = self.regs.get(src)
        self.load(src,reg)
        self.save(reg,dest)

    def gen_arith(self, op,a,b,r):
        r1 = self.regs.get("opA_"+r)
        r2 = self.regs.get("opB_"+r)
        rd = self.regs.get(r)
        self.load(a,r1)
        self.load(b,r2)
        if op=="+": self.emit(f"    add {rd}, {r1}, {r2}")
        if op=="-": self.emit(f"    sub {rd}, {r1}, {r2}")
        if op=="*": self.emit(f"    mul {rd}, {r1}, {r2}")
        self.save(rd,r)

    def gen_compare(self, op,a,b,r):
        r1 = self.regs.get("cmpA_"+r)
        r2 = self.regs.get("cmpB_"+r)
        rd = self.regs.get(r)
        self.load(a,r1)
        self.load(b,r2)
        tmp = self.regs.get("tmp_"+r)

        if op=="<":  self.emit(f"    slt {rd}, {r1}, {r2}")
        elif op==">":
            self.emit(f"    slt {rd}, {r2}, {r1}")
        elif op=="<=":
            self.emit(f"    slt {tmp}, {r2}, {r1}")
            self.emit(f"    xori {rd}, {tmp}, 1")
        elif op==">=":
            self.emit(f"    slt {tmp}, {r1}, {r2}")
            self.emit(f"    xori {rd}, {tmp}, 1")
        elif op=="==":
            self.emit(f"    sub {tmp}, {r1}, {r2}")
            self.emit(f"    sltiu {rd}, {tmp}, 1")
        elif op=="!=":
            self.emit(f"    sub {tmp}, {r1}, {r2}")
            self.emit(f"    sltu {rd}, $zero, {tmp}")

        self.save(rd,r)

    def gen_iftrue(self, cond, label):
        r = self.regs.get(cond)
        self.load(cond,r)
        self.emit(f"    bne {r}, $zero, {label}")

    def gen_iffalse(self, cond, label):
        r = self.regs.get(cond)
        self.load(cond,r)
        self.emit(f"    beq {r}, $zero, {label}")

    def gen_print(self, val):
        r = self.regs.get("print")
        self.load(val,r)
        self.emit(f"    move $a0, {r}")
        self.emit("    li $v0, 1")
        self.emit("    syscall")

    def gen_call(self, func):
        self.emit(f"    jal {func}")

    def gen_move_ret(self, dest):
        reg = self.regs.get(dest)
        self.emit(f"    move {reg}, $v0")
        self.save(reg,dest)

    def gen_ret(self, val):
        if val is not None:
            self.load(val,"$v0")
        self.emit("    jr $ra")

    def gen_enter(self, size):
        self.emit(f"    addi $sp, $sp, -{size}")
        self.emit("    move $fp, $sp")

    def gen_push(self, what):
        self.emit("    addi $sp, $sp, -4")
        if what == "FP":
            self.emit("    sw $fp, 0($sp)")
        else:
            r = self.regs.get(what)
            self.load(what,r)
            self.emit(f"    sw {r}, 0($sp)")

    def gen_pop(self, what):
        if what == "FP":
            self.emit("    lw $fp, 0($sp)")
            self.emit("    addi $sp, $sp, 4")
        else:
            r = self.regs.get(what)
            self.emit(f"    lw {r}, 0($sp)")
            self.emit("    addi $sp, $sp, 4")

    # ---------- Arrays & length ----------

    def gen_length(self, arr, dest):
        """
        dest = length(arr)
        Llamamos al runtime: cs_array_len(array) -> v0
        a0 = array pointer
        """
        r_arr = self.regs.get("len_arr")
        self.load(arr, r_arr)
        self.emit(f"    move $a0, {r_arr}")
        self.emit("    jal cs_array_len")
        rd = self.regs.get(dest)
        self.emit(f"    move {rd}, $v0")
        self.save(rd, dest)

    def gen_getidx(self, arr, idx, dest):
        """
        dest = arr[idx]
        runtime: cs_array_get(a0=array, a1=index) -> v0
        """
        r_arr = self.regs.get("getidx_arr")
        r_idx = self.regs.get("getidx_idx")
        self.load(arr, r_arr)
        self.load(idx, r_idx)
        self.emit(f"    move $a0, {r_arr}")
        self.emit(f"    move $a1, {r_idx}")
        self.emit("    jal cs_array_get")
        rd = self.regs.get(dest)
        self.emit(f"    move {rd}, $v0")
        self.save(rd, dest)

    # ---------- Objetos (stub) ----------

    def gen_alloc(self, type_name, dest):
        """
        dest = alloc Type
        Por ahora: llamamos a cs_alloc_object(type_id)
        y dejamos TODO para mapear nombres -> IDs.
        """
        self.emit(f"    # alloc {type_name} -> {dest}")
        # TODO: mapear type_name a un ID numérico
        self.emit("    li $a0, 0   # [TODO] type_id para objetos")
        self.emit("    jal cs_alloc_object")
        rd = self.regs.get(dest)
        self.emit(f"    move {rd}, $v0")
        self.save(rd, dest)

    def gen_getprop(self, obj, prop_name, dest):
        """
        dest = obj.prop_name
        Llamamos a cs_getprop(obj, prop_id)
        """
        self.emit(f"    # getprop {obj}.{prop_name} -> {dest}")
        r_obj = self.regs.get("obj_" + str(dest))
        self.load(obj, r_obj)

        # TODO: mapear prop_name -> offset/id
        self.emit("    li $a1, 0   # [TODO] prop_id para campos")
        self.emit(f"    move $a0, {r_obj}")
        self.emit("    jal cs_getprop")
        rd = self.regs.get(dest)
        self.emit(f"    move {rd}, $v0")
        self.save(rd, dest)

    # ---------- Exceptions / try-catch ----------

    def gen_try_begin(self, handler_label):
        """
        try_begin Lx  => push handler address
        runtime: cs_push_handler(a0 = &Lx)
        """
        self.emit(f"    la  $a0, {handler_label}")
        self.emit("    jal cs_push_handler")

    def gen_try_end(self):
        """
        try_end => pop handler
        runtime: cs_pop_handler()
        """
        self.emit("    jal cs_pop_handler")

    def gen_catch_begin(self, err_var, end_label):
        """
        catch_begin err, Lx
        - la excepción ya hizo salto hasta aquí
        - podemos guardar info del error si queremos
        (por ahora sólo comentario)
        """
        self.emit(f"    # catch_begin {err_var}, {end_label}")
        # TODO: last_error_code en err_var

    def gen_catch_end(self, end_label):
        """
        catch_end ... Lx => saltar al final del try/catch
        """
        self.emit(f"    j {end_label}")