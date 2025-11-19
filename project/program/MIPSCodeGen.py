from IR import Instr
from MIPSPrint import MIPSPrint
from MIPSStrings import MIPSStrings
from MIPSVar import MIPSVar
from SymbolTable import VariableSymbol
from TempManager import TempManager
from MIPSArrays import MIPSArrays

class MIPSCodeGen:
    def __init__(self, quads, symtab):
        self.quads = quads
        self.lines = []
        self.symtab = symtab

        # pool de strings
        self.string_pool = {}
        self.literal_labels = {}
        self.global_data = []

        # temporales
        self.temp_string = {}   # tX -> label de string literal
        self.temp_int = {}      # tX -> entero constante (cuando se conozca)
        self.temp_ptr = {}      # tX -> registro con puntero (strings/arrays)
        self.ptr_table = {}     # tX -> registro (principal para punteros)

        # módulos
        self.print_mod = MIPSPrint(self)
        self.strings_mod = MIPSStrings(self)
        self.vars_mod = MIPSVar(self)
        self.arrays_mod = MIPSArrays(self)
        self.tm = TempManager()

    def emit(self, line=""):
        self.lines.append(line)

    # ==========================================
    # registrar variables globales
    # ==========================================
    def _register_globals(self):
        for name, symbol in self.symtab.global_scope.symbols.items():
            if isinstance(symbol, VariableSymbol):
                self.vars_mod.register_global(name, symbol)

    # ==========================================
    # STRING LITERALS
    # ==========================================
    def _add_string_literal(self, literal):
        if literal in self.literal_labels:
            return self.literal_labels[literal]

        text = literal[1:-1]
        label = f"str_{len(self.string_pool)}"
        self.string_pool[label] = text
        self.literal_labels[literal] = label
        return label

    def _first_pass(self):
        for instr in self.quads:
            if instr.op == "copy" and isinstance(instr.a, str) and instr.a.startswith('"'):
                self._add_string_literal(instr.a)

    # ==========================================
    # DATA
    # ==========================================
    def _gen_data(self):
        self.emit(".data")

        # Primero las variables globales
        for line in self.global_data:
            self.emit(line)

        # Luego los strings literales
        for label, text in self.string_pool.items():
            self.emit(f'{label}: .asciiz "{text}"')

        # Strings auxiliares para prints
        self.emit('nl: .asciiz "\\n"')
        self.emit('str_lbr: .asciiz "["')
        self.emit('str_rbr: .asciiz "]"')
        self.emit('str_comma: .asciiz ", "')
        self.emit('str_array: .asciiz "[array]"')

        self.emit("")

    # ==========================================
    # TEXT
    # ==========================================
    def _gen_text(self):
        # reset
        self.temp_string = {}
        self.temp_int = {}
        self.temp_ptr = {}
        self.ptr_table = {}

        self.emit(".text")
        self.emit(".globl main")

        for instr in self.quads:
            op, a, b, r = instr.op, instr.a, instr.b, instr.r

            # ---------------- label ----------------
            if op == "label":
                self.emit(f"{a}:")

            # ---------------- copy -----------------
            elif op == "copy":
                if isinstance(a, str) and a.startswith('"'):
                    # string literal
                    label = self._add_string_literal(a)
                    self.temp_string[r] = label
                    self.temp_int.pop(r, None)
                    self.temp_ptr.pop(r, None)
                    self.ptr_table.pop(r, None)

                elif isinstance(a, int) or (isinstance(a, str) and a.isdigit()):
                    # entero inmediato
                    self.temp_int[r] = int(a)
                    self.temp_string.pop(r, None)
                    self.temp_ptr.pop(r, None)
                    self.ptr_table.pop(r, None)

                elif isinstance(a, str) and a in self.ptr_table:
                    # copiar puntero entre temporales: r = a
                    reg = self.ptr_table[a]
                    self.ptr_table[r] = reg
                    self.temp_ptr[r] = reg
                    self.temp_string.pop(r, None)
                    self.temp_int.pop(r, None)
                else:
                    # cualquier otra cosa: limpia marcas
                    self.temp_string.pop(r, None)
                    self.temp_int.pop(r, None)
                    self.temp_ptr.pop(r, None)
                    self.ptr_table.pop(r, None)

            # ---------------- print -----------------
            elif op == "print":
                self.print_mod.handle_print(a)

            # ---------------- ret -------------------
            elif op == "ret":
                self.emit("    li $v0, 10")
                self.emit("    syscall")

            # ------------ string concat (+) ---------
            elif op == "+":
                if a in self.temp_string and b in self.temp_string:
                    self.strings_mod.concat_strings(a, b, r)
                else:
                    raise Exception("Operador + solo implementado para strings por ahora")

            # ------------ arrays --------------------
            elif op == "alloc_array":
                # a = tamaño, r = tArr
                self.arrays_mod.alloc_array(a, r)

            elif op == "setidx":
                # a = tArr, b = index, r = tVal
                self.arrays_mod.set_index(a, b, r)

            elif op == "getidx":
                # a = tArr, b = index, r = tDst
                self.arrays_mod.get_index(a, b, r)

            elif op == "array_length":
                # a = tArr, r = tLen
                self.arrays_mod.length(a, r)

            # ------------ loadvar global ------------
            elif op == "loadvar":
                sym = self.symtab.global_scope.resolve(a)
                reg = self.tm.get_reg(r)

                if sym.type.name in ("int", "bool"):
                    self.emit(f"    la {reg}, {a}")
                    self.emit(f"    lw {reg}, 0({reg})")
                    self.temp_int[r] = 0   # marcar como entero "runtime"
                    self.temp_ptr.pop(r, None)
                    self.ptr_table.pop(r, None)

                elif sym.type.name == "string":
                    self.emit(f"    la {reg}, {a}")
                    self.emit(f"    lw {reg}, 0({reg})")
                    self.temp_ptr[r] = reg
                    self.ptr_table[r] = reg
                    self.temp_int.pop(r, None)
                    self.temp_string.pop(r, None)

                elif sym.type.name == "array":
                    self.emit(f"    la {reg}, {a}")
                    self.emit(f"    lw {reg}, 0({reg})")
                    self.temp_ptr[r] = reg
                    self.ptr_table[r] = reg
                    self.temp_int.pop(r, None)
                    self.temp_string.pop(r, None)

                else:
                    raise Exception("Tipo global no soportado en loadvar")

            # otros ops los ignoramos por ahora
            else:
                pass

    # ==========================================
    # PUBLIC API
    # ==========================================
    def generate(self):
        self.lines = []
        self.string_pool = {}
        self.literal_labels = {}

        self._first_pass()
        self._register_globals()
        self._gen_data()
        self._gen_text()

        return "\n".join(self.lines)
