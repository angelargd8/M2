from IR import Instr
from MIPSPrint import MIPSPrint
from MIPSStrings import MIPSStrings

class MIPSCodeGen:
    def __init__(self, quads):
        self.quads = quads
        self.lines = []

        # pool de strings
        self.string_pool = {}
        self.literal_labels = {}

        # mapeos locales
        self.temp_string = {}
        self.temp_int = {}

        # punteros dinámicos (runtime)
        self.runtime_ptrs = {}   # <- NUEVO
        self.temp_ptr = {}       # <- NUEVO

        # módulos
        self.print_mod = MIPSPrint(self)
        self.strings_mod = MIPSStrings(self)


    def emit(self, line=""):
        self.lines.append(line)

    # ============================================================
    # STRING LITERALS POOL
    # ============================================================
    def _add_string_literal(self, literal):
        """
        literal: incluye comillas, ej: "\"Hello world\""
        Reutiliza label si ya existía ese literal.
        """
        if literal in self.literal_labels:
            return self.literal_labels[literal]

        text = literal[1:-1]  # sin comillas
        label = f"str_{len(self.string_pool)}"
        self.string_pool[label] = text
        self.literal_labels[literal] = label
        return label

    def _first_pass(self):
        """
        Solo asegura que TODOS los literales de strings
        queden en string_pool antes de generar la sección .data.
        """
        for instr in self.quads:
            if instr.op == "copy" and isinstance(instr.a, str) and instr.a.startswith('"'):
                self._add_string_literal(instr.a)

    # ============================================================
    # DATA SECTION
    # ============================================================
    def _gen_data(self):
        self.emit(".data")
        for label, text in self.string_pool.items():
            self.emit(f'{label}: .asciiz "{text}"')
        self.emit('nl: .asciiz "\\n"')
        self.emit("")

    # ============================================================
    # TEXT SECTION
    # ============================================================
    def _gen_text(self):
        # Reseteamos mapeos por si acaso
        self.temp_string = {}
        self.temp_int = {}

        self.emit(".text")
        self.emit(".globl main")

        for instr in self.quads:
            op, a, b, r = instr.op, instr.a, instr.b, instr.r

            if op == "label":
                self.emit(f"{a}:")

            elif op == "copy":
                # copy de string literal: tX = "texto"
                if isinstance(a, str) and a.startswith('"'):
                    label = self._add_string_literal(a)
                    self.temp_string[r] = label
                    # si antes era entero, lo limpiamos
                    if r in self.temp_int:
                        del self.temp_int[r]

                # copy de literal entero: tX = 1
                elif isinstance(a, int) or (isinstance(a, str) and a.isdigit()):
                    self.temp_int[r] = int(a)
                    # si antes era string, lo limpiamos
                    if r in self.temp_string:
                        del self.temp_string[r]

                # otros tipos (más adelante: temporales, expresiones, etc.)
                else:
                    # por ahora solo limpiamos posibles registros
                    if r in self.temp_string:
                        del self.temp_string[r]
                    if r in self.temp_int:
                        del self.temp_int[r]

            elif op == "print":
                self.print_mod.handle_print(a)

            elif op == "ret":
                # salida simple
                self.emit("    li $v0, 10")
                self.emit("    syscall")

            elif op == "+":
                # concatenación real de strings dinámicos
                if a in self.temp_string and b in self.temp_string:
                    self.strings_mod.concat_strings(a, b, r)
                else:
                    raise Exception("Operador + solo implementado para strings por ahora")
                

            else:
                # otros ops los ignoramos por ahora
                pass

    # ============================================================
    # PUBLIC API
    # ============================================================
    def generate(self):
        # limpiamos por si se reusa el objeto
        self.lines = []
        self.string_pool = {}
        self.literal_labels = {}

        # 1) recolectar todos los literales para .data
        self._first_pass()

        # 2) escribir .data
        self._gen_data()

        # 3) escribir .text
        self._gen_text()

        return "\n".join(self.lines)
