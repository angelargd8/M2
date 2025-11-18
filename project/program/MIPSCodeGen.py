class MIPSCodeGen:
    """
    Generador MIPS corregido compatible con SPIM/QtSPIM.
    - Usa un pool de registros para temporales (t0..tN -> $t0..$t9 rotando)
    - Mueve todos los .asciiz a la sección .data
    - Evita immediates fuera de rango (no usa andi 0xFFFFFFFC)
    - Evita strings dentro de .text
    - Prefijos únicos para strings (LSTR)
    """

    def __init__(self, quads, symtab=None):
        self.quads = quads
        self.symtab = symtab

        self.text = []       # instrucciones MIPS (.text)
        self.data = []       # strings .asciiz (.data)
        self.label_counter = 0
        self.str_counter = 0

    # ------------------------------------------------------------
    # utilidades básicas
    # ------------------------------------------------------------

    def emit(self, s: str):
        self.text.append(s)

    def fresh(self) -> str:
        """Genera labels únicos para código."""
        self.label_counter += 1
        return f"LGEN{self.label_counter}"

    def fresh_str(self) -> str:
        """Genera labels únicos para strings en .data."""
        self.str_counter += 1
        return f"LSTR{self.str_counter}"

    def _reg_for_temp(self, tname: str) -> str:
        """
        Mapea un temporal lógico tN a un registro físico.
        Estrategia simple: rotar en el pool $t0..$t9 usando N % 10.
        """
        idx = int(tname[1:])  # quitar la 't'
        hw = idx % 10
        return f"$t{hw}"

    # ============================================================
    # RESOLUCIÓN DE VALORES
    # ============================================================

    def _resolve(self, x):
        """
        Convierte un operando textual a una tupla (kind, val):
        - ("reg",  "$t0")   : registro físico
        - ("fp",   offset)  : desplazamiento desde $fp
        - ("imm",  42)      : literal entero
        - ("label","LSTR1") : etiqueta (string o global)
        """

        # None / null -> 0
        if x is None or x == "None":
            return ("imm", 0)

        # TEMPORAL tN
        if isinstance(x, str) and x.startswith("t") and x[1:].isdigit():
            return ("reg", self._reg_for_temp(x))

        # FRAME POINTER FP[n] (offset lógico -> bytes)
        if isinstance(x, str) and x.startswith("FP["):
            off = int(x[3:-1]) * 4
            return ("fp", off)

        # STRING literal "..."
        if isinstance(x, str) and x.startswith('"') and x.endswith('"'):
            lbl = self.fresh_str()
            self.data.append(f'{lbl}: .asciiz {x}')
            return ("label", lbl)

        # LITERAL entero
        if isinstance(x, int):
            return ("imm", x)

        if isinstance(x, str) and x.isdigit():
            return ("imm", int(x))

        # null explícito
        if x == "null":
            return ("imm", 0)

        # Expresiones raras que NO deberían llegar aquí
        if "*" in str(x) or "[" in str(x) or "]" in str(x):
            raise Exception(f"_resolve: valor inválido en IR: {x}")

        # VARIABLE (global / local con offset)
        if isinstance(x, str):
            sym = self.symtab.lookup(x) if self.symtab else None
            if sym and hasattr(sym, "offset"):
                # offset lógico -> bytes
                return ("fp", sym.offset * 4)
            # tratar como global / label
            return ("label", x)

        raise Exception(f"_resolve: tipo no soportado en _resolve: {x} ({type(x)})")

    def _load(self, dest: str, x):
        kind, val = self._resolve(x)

        if kind == "imm":
            self.emit(f"li {dest}, {val}")
        elif kind == "reg":
            self.emit(f"move {dest}, {val}")
        elif kind == "fp":
            self.emit(f"lw {dest}, {val}($fp)")
        elif kind == "label":
            self.emit(f"la {dest}, {val}")
        else:
            raise Exception(f"_load: tipo desconocido: {kind}")

    def _store(self, src: str, x):
        # por si acaso
        if src == "$None":
            src = "$zero"

        kind, val = self._resolve(x)

        if kind == "fp":
            self.emit(f"sw {src}, {val}($fp)")
        elif kind == "label":
            # asumir que la etiqueta apunta a una palabra reservada
            self.emit(f"la $t9, {val}")
            self.emit(f"sw {src}, 0($t9)")
        else:
            raise Exception(f"_store: destino inválido para store: {x} (kind={kind})")

    # ============================================================
    # GENERADOR PRINCIPAL
    # ============================================================

    def generate(self) -> str:
        OP_MAP = {
            "+": "add",
            "-": "sub",
            "*": "mul",
            "/": "div",
            "%": "mod",

            "<": "lt",
            "<=": "le",
            ">": "gt",
            ">=": "ge",
            "==": "eq",
            "!=": "ne",

            "&&": "LogicalAnd",
            "||": "LogicalOr",
        }

        for instr in self.quads:
            op, a, b, r = instr.op, instr.a, instr.b, instr.r
            real_op = OP_MAP.get(op, op)

            handler = getattr(self, f"gen_{real_op}", None)
            if not handler:
                raise Exception(f"MIPSCodeGen: instrucción no soportada: {op}")
            handler(a, b, r)

        # =====================================================
        # ENSAMBLAR ARCHIVO FINAL
        # =====================================================

        final = []

        # ----- SECCIÓN .data -----
        if self.data:
            final.append(".data")
            final.extend(self.data)
            final.append("")

        # ----- SECCIÓN DE RUNTIME -----
        final.append("# include runtime (ya está cargado por separado)")
        final.append("")

        # ----- LAUNCHER PARA QTSPIM -----
        final.append(".text")
        # final.append(".globl __start")
        # final.append("__start:")
        # final.append("    jal main")
        # final.append("    li $v0, 10")
        # final.append("    syscall")
        # final.append("")


        # ----- CÓDIGO COMPILADO -----
        final.append(".globl main")
        final.append("")
        final.extend(self.text)

        return "\n".join(final)


    # ============================================================
    # LABEL
    # ============================================================

    def gen_label(self, a, b, r):
        self.emit(f"{a}:")
        # Prologue mínimo para main: usar el stack que QtSPIM ya pone en $sp
        if a == "main":
            self.emit("move $fp, $sp")

    # ============================================================
    # COPY / LOAD / STORE
    # ============================================================

    def gen_copy(self, a, b, r):
        self._load(self._reg_for_temp(r), a)

    def gen_load(self, a, b, r):
        self._load(self._reg_for_temp(r), a)

    def gen_store(self, a, b, r):
        # determinar registro fuente
        if isinstance(a, str) and a.startswith("t") and a[1:].isdigit():
            src = self._reg_for_temp(a)
        else:
            src = "$t0"
            self._load(src, a)

        self._store(src, r)

    # ============================================================
    # PRINT
    # ============================================================

    def gen_print(self, a, b, r):
        self._load("$a0", a)
        self.emit("jal cs_print")

    # ============================================================
    # PARAM / CALL / RET
    # ============================================================

    def gen_param(self, a, b, r):
        self._load("$t0", a)
        self.emit("addi $sp, $sp, -4")
        self.emit("sw $t0, 0($sp)")

    def gen_call(self, a, b, r):
        # llamada directa por label
        if isinstance(a, str) and not (a.startswith("t") and a[1:].isdigit()):
            self.emit(f"jal {a}")
        else:
            # llamada indirecta: a es un temporal tN
            kind, reg = self._resolve(a)
            if kind != "reg":
                raise Exception(f"gen_call: llamada indirecta con operando raro: {a}")
            # jalr usa $ra como link implícitamente
            self.emit(f"jalr {reg}")

        if r:
            self.emit(f"move {self._reg_for_temp(r)}, $v0")

        nargs = int(b) if b else 0
        if nargs > 0:
            self.emit(f"addi $sp, $sp, {nargs * 4}")

    def gen_ret(self, a, b, r):
        if a:
            self._load("$v0", a)
        self.emit("jr $ra")

    # ============================================================
    # ARITMÉTICAS
    # ============================================================

    def gen_add(self, a, b, r):
        self._binary("addu", a, b, r)

    def gen_sub(self, a, b, r):
        self._binary("subu", a, b, r)

    def gen_mul(self, a, b, r):
        self._binary("mul", a, b, r)

    def gen_div(self, a, b, r):
        self._binary_div(a, b, r)

    def gen_mod(self, a, b, r):
        self._binary_mod(a, b, r)

    def _binary(self, op, a, b, r):
        self._load("$t0", a)
        self._load("$t1", b)
        self.emit(f"{op} {self._reg_for_temp(r)}, $t0, $t1")

    def _binary_div(self, a, b, r):
        self._load("$t0", a)
        self._load("$t1", b)
        self.emit("div $t0, $t1")
        self.emit(f"mflo {self._reg_for_temp(r)}")

    def _binary_mod(self, a, b, r):
        self._load("$t0", a)
        self._load("$t1", b)
        self.emit("div $t0, $t1")
        self.emit(f"mfhi {self._reg_for_temp(r)}")

    # ============================================================
    # RELACIONALES / LÓGICAS
    # ============================================================

    def gen_lt(self, a, b, r):
        self._binary("slt", a, b, r)

    def gen_le(self, a, b, r):
        # a <= b  <=>  !(b < a)
        self._binary("slt", b, a, r)
        self.emit(f"xori {self._reg_for_temp(r)}, {self._reg_for_temp(r)}, 1")

    def gen_gt(self, a, b, r):
        self._binary("slt", b, a, r)

    def gen_ge(self, a, b, r):
        self._binary("slt", a, b, r)
        self.emit(f"xori {self._reg_for_temp(r)}, {self._reg_for_temp(r)}, 1")

    def gen_eq(self, a, b, r):
        self._binary("xor", a, b, r)
        self.emit(f"sltiu {self._reg_for_temp(r)}, {self._reg_for_temp(r)}, 1")

    def gen_ne(self, a, b, r):
        self._binary("xor", a, b, r)
        self.emit(
            f"sltu {self._reg_for_temp(r)}, $zero, {self._reg_for_temp(r)}"
        )

    def gen_LogicalAnd(self, a, b, r):
        self._binary("and", a, b, r)

    def gen_LogicalOr(self, a, b, r):
        self._binary("or", a, b, r)

    # ============================================================
    # GOTO / BRANCHES
    # ============================================================

    def gen_goto(self, a, b, r):
        self.emit(f"j {r}")

    def gen_iftrue_goto(self, a, b, r):
        self._load("$t0", a)
        self.emit(f"bne $t0, $zero, {r}")

    def gen_iffalse_goto(self, a, b, r):
        self._load("$t0", a)
        self.emit(f"beq $t0, $zero, {r}")

    # ============================================================
    # ARRAYS
    # ============================================================

    def gen_alloc_array(self, a, b, r):
        self._load("$a0", a)
        self.emit("jal cs_array_new")
        self.emit(f"move {self._reg_for_temp(r)}, $v0")

    def gen_setidx(self, a, b, r):
        self._load("$a0", a)
        self._load("$a1", b)
        self._load("$a2", r)
        self.emit("jal cs_array_set")

    def gen_getidx(self, a, b, r):
        self._load("$a0", a)
        self._load("$a1", b)
        self.emit("jal cs_array_get")
        self.emit(f"move {self._reg_for_temp(r)}, $v0")

    def gen_array_length(self, a, b, r):
        self._load("$a0", a)
        self.emit("jal cs_array_len")
        self.emit(f"move {self._reg_for_temp(r)}, $v0")

    # ============================================================
    # OBJETOS
    # ============================================================

    def gen_setprop(self, a, b, r):
        lbl = self.fresh_str()
        self.data.append(f'{lbl}: .asciiz "{b}"')
        self._load("$a0", a)
        self.emit(f"la $a1, {lbl}")
        self._load("$a2", r)
        self.emit("jal cs_setprop")

    def gen_getprop(self, a, b, r):
        lbl = self.fresh_str()
        self.data.append(f'{lbl}: .asciiz "{b}"')
        self._load("$a0", a)
        self.emit(f"la $a1, {lbl}")
        self.emit("jal cs_getprop")
        self.emit(f"move {self._reg_for_temp(r)}, $v0")

    # ============================================================
    # EXCEPCIONES
    # ============================================================

    def gen_push_handler(self, a, b, r):
        self.emit(f"la $a0, {a}")
        self.emit("jal cs_push_handler")

    def gen_pop_handler(self, a, b, r):
        self.emit("jal cs_pop_handler")

    def gen_get_exception(self, a, b, r):
        self.emit("jal cs_get_exception")
        self.emit(f"move {self._reg_for_temp(r)}, $v0")

    def gen_throw(self, a, b, r):
        self.emit("jal cs_throw")

    def gen_newobj(self, a, b, r):
        """
        IR: newobj className, -, tX
        produce:
        a0 = sizeof(object)   # siempre 8 bytes (vtable + slot)
        jal cs_alloc_object
        move tX, v0
        Luego llamar al constructor implícito si existe
        """

        class_name = a  # string con el nombre de la clase

        # 1) reservar objeto = cs_alloc_object()
        self.emit("li $a0, 8")
        self.emit("jal cs_alloc_object")
        dest = self._reg_for_temp(r)
        self.emit(f"move {dest}, $v0")

        # 2) llamar a constructor si existe: _init_ClassName
        ctor = f"_init_{class_name}"
        self.emit(f"la $t0, {ctor}")
        self.emit(f"move $a0, {dest}")   # this como param
        self.emit("jalr $t0")
