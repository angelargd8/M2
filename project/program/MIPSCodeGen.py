from IR import Instr
from MIPSPrint import MIPSPrint
from MIPSStrings import MIPSStrings
from MIPSVar import MIPSVar
from SymbolTable import VariableSymbol, FunctionSymbol
from TempManager import TempManager
from MIPSArrays import MIPSArrays
from MIPSFun import MIPSFun
from MIPSOp import MIPSOp
from MIPSSen import MIPSSen



class MIPSCodeGen:
    def __init__(self, quads, symtab):
        self.quads = quads
        self.lines = []
        self.symtab = symtab

        # pool de strings literales .data
        self.string_pool = {}
        self.literal_labels = {}
        self.global_data = []

        # info de temporales
        self.temp_string = {}   # tX -> label de string literal
        self.temp_int = {}      # tX -> entero constante (cuando se conozca)
        self.temp_float = {}    # tX -> float constante (cuando se conozca)
        self.temp_bool = {}     # tX -> booleano constante (cuando se conozca)
        self.temp_ptr = {}      # tX -> registro con puntero (strings/arrays)
        self.ptr_table = {}     # tX -> registro (principal para punteros)

        # funciones conocidas (para decidir prolog/epilog)
        self.func_labels = set()

        # módulos auxiliares
        self.tm = TempManager()
        self.print_mod = MIPSPrint(self)
        self.strings_mod = MIPSStrings(self)
        self.vars_mod = MIPSVar(self)
        self.arrays_mod = MIPSArrays(self)
        
        self.fun_mod = MIPSFun(self)
        self.sen_mod = MIPSSen(self)
        self.op_mod = MIPSOp(self)

    def emit(self, line=""):
        self.lines.append(line)

    # ==========================================================
    # REGISTRO DE VARIABLES GLOBALES
    # ==========================================================
    def _register_globals(self):
        """
        Antes: sólo registrábamos globales con inicializador literal,
        y las que tenían inicializador "complejo" (llamadas a funciones,
        expresiones, etc.) se saltaban → el label nunca existía.

        Ahora: TODA VariableSymbol del scope global se registra,
        aunque el valor inicial sea complejo. En esos casos, simplemente
        queda .word 0 y el valor real se escribe en tiempo de ejecución.
        """
        for name, symbol in self.symtab.global_scope.symbols.items():
            if isinstance(symbol, VariableSymbol):
                # Delega la lógica del .data a MIPSVar
                self.vars_mod.register_global(name, symbol)

    # ==========================================================
    # STRING LITERALS
    # ==========================================================
    def _add_string_literal(self, literal):
        if literal in self.literal_labels:
            return self.literal_labels[literal]

        text = literal[1:-1]  # quitar comillas
        label = f"str_{len(self.string_pool)}"
        self.string_pool[label] = text
        self.literal_labels[literal] = label
        return label

    def _first_pass(self):
        for instr in self.quads:
            if instr.op == "copy" and isinstance(instr.a, str) and instr.a.startswith('"'):
                self._add_string_literal(instr.a)

    # ==========================================================
    # SECCIÓN .data
    # ==========================================================
    def _gen_data(self):
        self.emit(".data")

        # variables globales (llenadas desde MIPSVar.register_global)
        for line in self.global_data:
            self.emit(line)

        # strings literales
        for label, text in self.string_pool.items():
            self.emit(f'{label}: .asciiz "{text}"')

        # strings auxiliares
        self.emit('nl: .asciiz "\\n"')
        self.emit('str_lbr: .asciiz "["')
        self.emit('str_rbr: .asciiz "]"')
        self.emit('str_comma: .asciiz ", "')
        self.emit('str_array: .asciiz "[array]"')
        self.emit("")

    # ==========================================================
    # RUNTIME EMBEBIDO: cs_int_to_string
    # ==========================================================
    def _emit_runtime_support(self):
        self.emit("")
        self.emit("# ===== RUNTIME SUPPORT: cs_int_to_string =====")
        self.emit("cs_int_to_string:")
        self.emit("    addi $sp, $sp, -12")
        self.emit("    sw $ra, 8($sp)")
        self.emit("    sw $s0, 4($sp)")
        self.emit("    sw $s1, 0($sp)")
        self.emit("    move $s1, $a0")   # guardar entero original en s1
        self.emit("    li $a0, 12")
        self.emit("    li $v0, 9")
        self.emit("    syscall")
        self.emit("    move $s0, $v0        # base buffer")
        self.emit("    addi $t0, $s0, 11")
        self.emit("    sb $zero, 11($s0)")
        self.emit("    move $t2, $s1")
        self.emit("    bne $t2, $zero, cs_its_nonzero")
        self.emit("    li $t3, '0'")
        self.emit("    sb $t3, 10($s0)")
        self.emit("    addi $v0, $s0, 10")
        self.emit("    j cs_its_done")
        self.emit("cs_its_nonzero:")
        self.emit("    li $t4, 0")
        self.emit("    bltz $t2, cs_its_neg")
        self.emit("    j cs_its_abs_ok")
        self.emit("cs_its_neg:")
        self.emit("    li $t4, 1")
        self.emit("    subu $t2, $zero, $t2")
        self.emit("cs_its_abs_ok:")
        self.emit("    move $t1, $t0")
        self.emit("cs_its_digit_loop:")
        self.emit("    beq $t2, $zero, cs_its_digits_done")
        self.emit("    li $t5, 10")
        self.emit("    div $t2, $t5")
        self.emit("    mfhi $t6")
        self.emit("    mflo $t2")
        self.emit("    addi $t6, $t6, 48")
        self.emit("    sb $t6, -1($t1)")
        self.emit("    addi $t1, $t1, -1")
        self.emit("    j cs_its_digit_loop")
        self.emit("cs_its_digits_done:")
        self.emit("    beq $t4, $zero, cs_its_no_minus")
        self.emit("    li $t7, '-'")
        self.emit("    sb $t7, -1($t1)")
        self.emit("    addi $t1, $t1, -1")
        self.emit("cs_its_no_minus:")
        self.emit("    move $v0, $t1")
        self.emit("cs_its_done:")
        self.emit("    lw $s1, 0($sp)")
        self.emit("    lw $s0, 4($sp)")
        self.emit("    lw $ra, 8($sp)")
        self.emit("    addi $sp, $sp, 12")
        self.emit("    jr $ra")
        self.emit("")

    # ==========================================================
    # SECCIÓN .text
    # ==========================================================
    def _gen_text(self):
        self.temp_string = {}
        self.temp_int = {}
        self.temp_ptr = {}
        self.ptr_table = {}

        self.emit(".text")
        self.emit(".globl main")
        self.emit(".globl cs_int_to_string")

        self._emit_runtime_support()

        for instr in self.quads:
            op, a, b, r = instr.op, instr.a, instr.b, instr.r

            # ---------- LABEL ----------
            if op == "label":
                self.emit(f"{a}:")
                if a in self.func_labels:
                    self.fun_mod.emit_prolog(a)

            # ---------- COPY ----------
            elif op == "copy":
                if isinstance(a, str) and a.startswith('"'):
                    label = self._add_string_literal(a)
                    self.temp_string[r] = label
                    self.temp_int.pop(r, None)
                    self.temp_ptr.pop(r, None)
                    self.ptr_table.pop(r, None)

                elif isinstance(a, int) or (isinstance(a, str) and a.isdigit()):
                    self.temp_int[r] = int(a)
                    self.temp_string.pop(r, None)
                    self.temp_ptr.pop(r, None)
                    self.ptr_table.pop(r, None)

                elif isinstance(a, str) and a in self.ptr_table:
                    reg = self.ptr_table[a]
                    self.ptr_table[r] = reg
                    self.temp_ptr[r] = reg
                    self.temp_string.pop(r, None)
                    self.temp_int.pop(r, None)

                elif isinstance(a, float):
                    self.temp_float[r] = a  # constante verdadera
                    self.temp_int.pop(r, None)
                    self.temp_string.pop(r, None)
                    self.temp_ptr.pop(r, None)

                else:
                    self.temp_string.pop(r, None)
                    self.temp_int.pop(r, None)
                    self.temp_ptr.pop(r, None)
                    self.ptr_table.pop(r, None)

            # ---------- PRINT ----------
            elif op == "print":
                self.print_mod.handle_print(a)

            # ---------- FUNCIONES ----------
            elif op == "param":
                self.fun_mod.emit_param(a)

            elif op == "call":
                self.fun_mod.emit_call(a, b, r)

            elif op == "ret":
                self.fun_mod.emit_ret(a)

            # ---------- LOAD / STORE FP[...] ----------
            elif op == "load":
                self._load_from_addr(a, self.tm.get_reg(r))

            elif op == "store":
                self._store_to_addr(a, r)

            elif op == "store_global":
                sym = self.symtab.global_scope.resolve(r)
                label = sym.mips_label                       # <<<<< usa el label seguro

                if sym.type.name == "float":
                    # float → float
                    if a in self.temp_float:
                        f = self.tm.get_freg(a)
                        if self.temp_float[a] is not None:
                            self.emit(f"    li.s {f}, {self.temp_float[a]}")
                            self.temp_float[a] = None
                        self.emit(f"    la $t9, {label}")
                        self.emit(f"    s.s {f}, 0($t9)")
                    else:
                        # int → float
                        ri = self.tm.get_reg(a)
                        rf = self.tm.get_freg(a)
                        self._load(a, ri)
                        self.emit(f"    mtc1 {ri}, {rf}")
                        self.emit(f"    cvt.s.w {rf}, {rf}")
                        self.emit(f"    la $t9, {label}")
                        self.emit(f"    s.s {rf}, 0($t9)")

                else:
                    # int / bool / string pointer
                    reg = self.tm.get_reg(a)
                    self._load(a, reg)
                    self.emit(f"    la $t9, {label}")
                    self.emit(f"    sw {reg}, 0($t9)")


            elif op in ["-", "*", "/", "%"]:
                self.op_mod.arithmetic(op, a, b, r)

            elif op in ["<", "<=", ">", ">=", "==", "!="]:
                self.op_mod.comparison(op, a, b, r)

            elif op in ["&&", "||"]:
                self.op_mod.logical(op, a, b, r)

            elif op == "not":
                self.op_mod.unary_not(a, r)

            elif op == "+":

                # Si alguno de los operandos es string (literal, dinámico o var string),
                # usamos la lógica de concatenación.
                if self._is_string(a) or self._is_string(b):
                    self._concat_strings(a, b, r)
                else:
                    # Caso numérico puro: delegamos a MIPSOp.arithmetic
                    self.op_mod.arithmetic("+", a, b, r)

            # ---------- ARRAYS ----------
            elif op == "alloc_array":
                self.arrays_mod.alloc_array(a, r)
            elif op == "setidx":
                self.arrays_mod.set_index(a, b, r)
            elif op == "getidx":
                self.arrays_mod.get_index(a, b, r)
            elif op == "array_length":
                self.arrays_mod.length(a, r)

            # sentencias de control
            elif op == "iftrue_goto":
                self.sen_mod.iftrue(a, r)

            elif op == "iffalse_goto":
                self.sen_mod.iffalse(a, r)

            elif op == "goto":
                self.sen_mod.goto(r)

            # ---------- LOADVAR (globales) ----------
            
            elif op == "loadvar":
                sym = self.symtab.global_scope.resolve(a)
                label = sym.mips_label                       # <<<<<< etiqueta segura (g_a, g_b, etc.)
                reg = self.tm.get_reg(r)

                # int/bool
                if sym.type.name in ("int", "bool"):
                    self.emit(f"    la {reg}, {label}")
                    self.emit(f"    lw {reg}, 0({reg})")

                    # limpiar metadatos
                    self.temp_int.pop(r, None)
                    self.temp_string.pop(r, None)
                    self.temp_ptr.pop(r, None)
                    self.ptr_table.pop(r, None)


    # ==========================================================
    # LABELS DE FUNCIONES
    # ==========================================================
    def _collect_function_labels(self):
        self.func_labels.add("main")
        for name, sym in self.symtab.global_scope.symbols.items():
            if isinstance(sym, FunctionSymbol):
                label = sym.label or sym.name
                self.func_labels.add(label)


    # ==========================================================
    # LOAD 
    # ======================s===================================
    def _load(self, src, dst_reg):
        """
        Carga src en dst_reg.
        src puede ser:
        - un literal numérico
        - un literal string
        - un temporal con int, float, ptr
        - un acceso FP[offset]
        - una variable global g_xxx
        """

        # 1) LITERALES NUMÉRICOS
        if isinstance(src, int) or (isinstance(src, str) and src.isdigit()):
            self.emit(f"    li {dst_reg}, {src}")
            return

        # 2) STRING LITERAL (temp_string)
        if src in self.temp_string:
            label = self.temp_string[src]
            self.emit(f"    la {dst_reg}, {label}")
            return

        # 3) PUNTERO DINÁMICO (ptr_table)
        if src in self.ptr_table:
            reg_ptr = self.ptr_table[src]
            self.emit(f"    move {dst_reg}, {reg_ptr}")
            return

        # 4) CONSTANTE ENTERA TEMPORAL
        if src in self.temp_int:
            val = self.temp_int[src]
            self.emit(f"    li {dst_reg}, {val}")
            return

        # 5) CONSTANTE FLOAT TEMPORAL
        if src in self.temp_float and self.temp_float[src] is not None:
            val = self.temp_float[src]
            self.emit(f"    li.s {dst_reg}, {val}")
            self.temp_float[src] = None
            return

        # 6) FRAME POINTER (FP[offset])
        if isinstance(src, str) and src.startswith("FP["):
            offset = int(src[3:-1])
            self.emit(f"    lw {dst_reg}, {offset}($fp)")
            return

        # 7) VARIABLE GLOBAL SEGURA g_xxx
        if isinstance(src, str) and src in self.symtab.global_scope.symbols:
            sym = self.symtab.global_scope.symbols[src]
            safe = getattr(sym, "mips_label", src)
            self.emit(f"    la $t9, {safe}")
            self.emit(f"    lw {dst_reg}, 0($t9)")
            return

        # 8) TEMPORAL SIN METADATA (asignarle registro)
        if isinstance(src, str):
            reg_src = self.tm.get_reg(src)
            self.emit(f"    move {dst_reg}, {reg_src}")
            return

        # SI NADA APLICA → ERROR
        raise Exception(f"_load: tipo no soportado para src={src} ({type(src)})")

    def _load_from_addr(self, addr, dst_reg):
        # addr viene en formato FP[offset] o nombre de variable global
        if addr.startswith("FP["):
            offset = int(addr[3:-1])
            self.emit(f"    lw {dst_reg}, {offset}($fp)")
        else:
            # variable global
            self.emit(f"    la {dst_reg}, {addr}")
            self.emit(f"    lw {dst_reg}, 0({dst_reg})")

    def _store_to_addr(self, value, addr):
        reg_val = self.tm.get_reg(value)
        self._load(value, reg_val)

        if addr.startswith("FP["):
            offset = int(addr[3:-1])
            self.emit(f"    sw {reg_val}, {offset}($fp)")
        else:
            # global
            self.emit(f"    la $t9, {addr}")
            self.emit(f"    sw {reg_val}, 0($t9)")

    def _is_string(self, t):
        return (
            t in self.temp_string or
            t in self.temp_ptr or
            (isinstance(t, str) and t.startswith('"'))
        )

    def _concat_strings(self, a, b, r):

        a_is_str = self._is_string(a)
        b_is_str = self._is_string(b)

        # caso 1: string + string (literal o dinámico)
        if a_is_str and b_is_str:
            self.strings_mod.concat_strings(a, b, r)
            return

        # caso 2: string + int
        if a_is_str and not b_is_str:
            reg_b = self.tm.get_reg(b)
            self._load(b, reg_b)

            self.emit(f"    move $a0, {reg_b}")
            self.emit("    jal cs_int_to_string")
            reg_tmp = self.tm.get_reg(r)
            self.emit(f"    move {reg_tmp}, $v0")

            self.temp_ptr[r] = reg_tmp
            self.ptr_table[r] = reg_tmp

            self.strings_mod.concat_strings(a, r, r)
            return

        # caso 3: int + string
        if b_is_str and not a_is_str:
            reg_a = self.tm.get_reg(a)
            self._load(a, reg_a)

            self.emit(f"    move $a0, {reg_a}")
            self.emit("    jal cs_int_to_string")
            reg_tmp = self.tm.get_reg(r)
            self.emit(f"    move {reg_tmp}, $v0")

            self.temp_ptr[r] = reg_tmp
            self.ptr_table[r] = reg_tmp

            self.strings_mod.concat_strings(r, b, r)
            return

        # caso inesperado
        raise Exception(f"Concatenación no soportada entre {a} y {b}")

    # ==========================================================
    # API PÚBLICA
    # ==========================================================
    def generate(self):
        self.lines = []
        self.string_pool = {}
        self.literal_labels = {}

        self._first_pass()
        self._register_globals()
        self._collect_function_labels()
        self._gen_data()
        self._gen_text()

        return "\n".join(self.lines)
