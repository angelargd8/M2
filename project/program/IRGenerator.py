from TempManager import TempManager
from IR import Instr
from SymbolTable import VariableSymbol, FunctionSymbol, TypeSymbol, SymbolTable  # ajusta si SymbolTable está en otro lado

# AST nodes
from AstNodes import *

class IRGenerator:
    """
    Genera código intermedio (quads / tres direcciones) a partir del AST.

    Trabaja sobre los nodos de astnodes.py y usa la SymbolTable que ya
    fue llenada por el SemanticAnalyzer (incluyendo:
      - FunctionSymbol.param_offsets
      - FunctionSymbol.local_offsets
      - frame_size
    )
    """

    def __init__(self, symtab: SymbolTable | None = None):
        self.quads: list[Instr] = []
        self.tm = TempManager()
        self.symtab = symtab

        # Pila de loops, para manejar break/continue
        # elementos: (label_start, label_end, label_update)
        self.loop_stack: list[tuple[str, str, str | None]] = []

        # clase actual (para métodos)
        self.current_class: str | None = None

        # función actual (FunctionSymbol)
        self.current_func: FunctionSymbol | None = None

    # ==================== utilidades ====================

    def emit(self, op, a=None, b=None, r=None):
        self.quads.append(Instr(op, a, b, r))

    def generate(self, node: Program):
        """
        Punto de entrada: recibe un AST Program.
        1) Genera primero todas las funciones y clases (labels).
        2) Luego genera el código "main" para el código toplevel.
        """
        self.quads = []

        # 1) funciones y clases
        for stmt in node.statements:
            if isinstance(stmt, ClassDecl):
                self._visit_ClassDecl(stmt)
            elif isinstance(stmt, FuncDecl):
                self._visit_FuncDecl(stmt)

        # 2) main para el código suelto
        self.emit("label", "main", None, None)
        for stmt in node.statements:
            if not isinstance(stmt, (FuncDecl, ClassDecl)):
                self._visit(stmt)

        # ret implícito al final de main
        self.emit("ret", "0", None, None)
        return self.quads

    # ------------- helpers de direcciones -------------

    def _addr_for_global_var(self, name: str) -> str:
        """
        Usa la SymbolTable.global_scope para encontrar un VariableSymbol global.
        Para variables globales de verdad, devolvemos el NOMBRE (label en .data).
        """
        if not self.symtab:
            return name
        sym = self.symtab.global_scope.resolve(name)
        if isinstance(sym, VariableSymbol):
            if sym.storage == "global":
                # variable global -> label en .data
                return sym.name
            else:
                # locals/params que por error estén en global_scope
                return f"FP[{sym.offset}]"
        return name

    def _current_func_symbol(self, name: str | None = None) -> FunctionSymbol | None:
        """
        Obtiene el FunctionSymbol de la función actual.
        Si name es None, devuelve self.current_func.
        Si no, intenta resolverlo con nombre simple o calificado (para métodos).
        """
        if not self.symtab:
            return None

        if name is None and self.current_func is not None:
            return self.current_func

        # si hay clase actual, intentar nombre calificado
        if self.current_class and name is not None:
            qname = f"{self.current_class}.{name}"
            s = self.symtab.global_scope.resolve(qname)
            if isinstance(s, FunctionSymbol):
                return s

        if name is not None:
            s = self.symtab.global_scope.resolve(name)
            if isinstance(s, FunctionSymbol):
                return s

        return None

    def _addr_for_local_var(self, name: str) -> str | None:
        """
        Usa FunctionSymbol.param_offsets y local_offsets para armar una dirección
        relativa a FP: 'FP[offset]'.
        """
        f = self._current_func_symbol()
        if not f:
            return None

        if f.param_offsets and name in f.param_offsets:
            off = f.param_offsets[name]
            return f"FP[{off}]"

        if f.local_offsets and name in f.local_offsets:
            off = f.local_offsets[name]
            # SEM: local_offsets guarda un número positivo; MIPSCodeGen decidirá cómo traducirlo
            return f"FP[{off}]"

        return None

    def _addr_for_var(self, name: str) -> str:
        """
        Determina si una variable es local/param o global, y devuelve su dirección simbólica.
        """
        # primero intentar como local/param de la función actual
        addr = self._addr_for_local_var(name)
        if addr is not None:
            return addr

        # si no, global
        return self._addr_for_global_var(name)

    def _load_var(self, name: str) -> str:
        """
        Carga el valor de una variable (global/local/param) en un temporal.
        """
        addr = self._addr_for_var(name)
        t = self.tm.new_temp()
        self.emit("load", addr, None, t)
        return t

    def _store_var(self, name: str, t_value: str):
        """
        Guarda el contenido de t_value en una variable (global/local/param).
        """
        sym = self.symtab.global_scope.resolve(name)
        # -------- GLOBAL --------
        if isinstance(sym, VariableSymbol) and sym.storage == "global":
            # store_global r -> name
            self.emit("store_global", t_value, None, name)
            return

        # -------- LOCAL/PARAM --------
        addr = self._addr_for_var(name)
        self.emit("store", t_value, None, addr)

    # ==================== dispatcher genérico ====================

    def _visit(self, node):
        if node is None:
            return None

        tname = node.__class__.__name__
        m = getattr(self, f"_visit_{tname}", None)
        if m:
            return m(node)

        # fallback: recorrer campos comunes si fuera necesario
        # (para este diseño, deberíamos tener implementado todo lo importante)
        return None

    # ==================== declaraciones top-level ====================

    def _visit_Program(self, node: Program):
        # No se usa directamente; generate maneja Program.
        for s in node.statements:
            self._visit(s)

    def _visit_VarDecl(self, node: VarDecl):
        """
        let / const a nivel global o local.
        """
        name = node.name

        # Si hay inicializador, evaluar y hacer store
        if node.init is not None:
            t_init = self._visit(node.init)
            self.tm.add_ref(t_init)
            self._store_var(name, t_init)
            self.tm.release_ref(t_init)
        # Si no tiene init: en IR no necesitamos hacer nada; runtime asume 0/null

    def _visit_FuncDecl(self, node: FuncDecl):
        """
        Función top-level o método de clase.
        - Usa FunctionSymbol para conseguir offsets de params/locales y label.
        """
        func_name = node.name
        f_sym = self._current_func_symbol(func_name)
        prev_func = self.current_func
        self.current_func = f_sym

        # label de función
        if f_sym and f_sym.label:
            label = f_sym.label
        elif self.current_class is not None:
            label = f"{self.current_class}.{func_name}"
        else:
            label = func_name

        self.emit("label", label, None, None)

        # Si es método de clase, podemos asumir 'this' en FP[8] o similar,
        # pero tu runtime lo maneja de forma más explícita vía new/props.
        # Aquí no hacemos nada especial, simplemente generamos el cuerpo.

        # cuerpo
        if isinstance(node.body, Block):
            self._visit_Block(node.body)
        else:
            # por si algún día soportas cuerpo como lista
            for s in node.body or []:
                self._visit(s)

        # ret implícito (para funciones void)
        self.emit("ret", None, None, None)

        self.current_func = prev_func

    def _visit_ClassDecl(self, node: ClassDecl):
        """
        Genera:
        - Un "constructor sintético" opcional que inicializa propiedades.
        - Código de los métodos.
        Aquí hacemos algo simple: sólo generamos métodos como funciones con label "Clase.metodo".
        """
        prev_class = self.current_class
        self.current_class = node.name

        # Métodos
        for m in node.methods or []:
            self._visit_FuncDecl(m)

        self.current_class = prev_class

    # ==================== statements ====================

    def _visit_Block(self, node: Block):
        for s in node.statements:
            self._visit(s)

    def _visit_Assign(self, node: Assign):
        # target puede ser Var, Member, Index
        t_value = self._visit(node.expr)
        self.tm.add_ref(t_value)

        if isinstance(node.target, Var):
            self._store_var(node.target.name, t_value)

        elif isinstance(node.target, Member):
            # obj.prop = expr;
            t_obj = self._visit(node.target.object)
            self.tm.add_ref(t_obj)
            self.emit("setprop", t_obj, node.target.name, t_value)
            self.tm.release_ref(t_obj)

        elif isinstance(node.target, Index):
            # seq[index] = expr;
            t_seq = self._visit(node.target.seq)
            t_idx = self._visit(node.target.index)
            self.tm.add_ref(t_seq)
            self.tm.add_ref(t_idx)
            self.emit("setidx", t_seq, t_idx, t_value)
            self.tm.release_ref(t_seq)
            self.tm.release_ref(t_idx)

        else:
            # fallback raro, pero para no explotar:
            pass

        self.tm.release_ref(t_value)

    def _visit_ExprStmt(self, node: ExprStmt):
        self._visit(node.expr)

    def _visit_PrintStmt(self, node: PrintStmt):
        # Caso 1: print de variable global (NO cargar a temporal)
        if isinstance(node.expr, Var):
            name = node.expr.name
            # Si está en global_scope → usar print directo
            if self.symtab and name in self.symtab.global_scope.symbols:
                self.emit("print", name, None, None)
                return

        # Caso 2: print de boolean literal
        if isinstance(node.expr, BooleanLiteral):
            val = 1 if node.expr.value else 0
            t = self.tm.new_temp()
            self.emit("copy", val, None, t)
            self.emit("print", t, None, None)
            return

        # Caso 3: expresión normal → evaluar, imprimir temporal
        t = self._visit(node.expr)
        self.tm.add_ref(t)
        self.emit("print", t, None, None)
        self.tm.release_ref(t)

    def _visit_If(self, node: If):
        t_cond = self._visit(node.condition)
        self.tm.add_ref(t_cond)

        lbl_else = self.tm.newLabel()
        lbl_end = self.tm.newLabel()

        self.emit("iffalse_goto", t_cond, None, lbl_else)
        self.tm.release_ref(t_cond)

        # then
        self._visit_Block(node.then_branch)

        if node.else_branch:
            self.emit("goto", None, None, lbl_end)
            self.emit("label", lbl_else, None, None)
            self._visit_Block(node.else_branch)
            self.emit("label", lbl_end, None, None)
        else:
            self.emit("label", lbl_else, None, None)

    def _visit_While(self, node: While):
        lbl_start = self.tm.newLabel()
        lbl_end = self.tm.newLabel()

        self.loop_stack.append((lbl_start, lbl_end, lbl_start))

        self.emit("label", lbl_start, None, None)
        t_cond = self._visit(node.condition)
        self.tm.add_ref(t_cond)
        self.emit("iffalse_goto", t_cond, None, lbl_end)
        self.tm.release_ref(t_cond)

        self._visit_Block(node.body)
        self.emit("goto", None, None, lbl_start)
        self.emit("label", lbl_end, None, None)

        self.loop_stack.pop()

    def _visit_DoWhile(self, node: DoWhile):
        lbl_start = self.tm.newLabel()
        lbl_end = self.tm.newLabel()

        self.loop_stack.append((lbl_start, lbl_end, lbl_start))

        self.emit("label", lbl_start, None, None)
        self._visit_Block(node.body)
        t_cond = self._visit(node.condition)
        self.tm.add_ref(t_cond)
        self.emit("iftrue_goto", t_cond, None, lbl_start)
        self.tm.release_ref(t_cond)
        self.emit("label", lbl_end, None, None)

        self.loop_stack.pop()

    def _visit_For(self, node: For):
        # for (init; condition; step) body
        lbl_start = self.tm.newLabel()
        lbl_end = self.tm.newLabel()
        lbl_update = self.tm.newLabel()

        self.loop_stack.append((lbl_start, lbl_end, lbl_update))

        if node.init is not None:
            self._visit(node.init)

        self.emit("label", lbl_start, None, None)
        if node.condition is not None:
            t_cond = self._visit(node.condition)
            self.tm.add_ref(t_cond)
            self.emit("iffalse_goto", t_cond, None, lbl_end)
            self.tm.release_ref(t_cond)

        self._visit_Block(node.body)

        self.emit("label", lbl_update, None, None)
        if node.step is not None:
            self._visit(node.step)
        self.emit("goto", None, None, lbl_start)
        self.emit("label", lbl_end, None, None)

        self.loop_stack.pop()

    def _visit_Foreach(self, node: Foreach):
        """
        foreach (name in iterable) { body }
        Descomponemos en un for con índice.
        """
        t_collection = self._visit(node.iterable)
        self.tm.add_ref(t_collection)

        lbl_start = self.tm.newLabel()
        lbl_end = self.tm.newLabel()
        lbl_update = self.tm.newLabel()
        self.loop_stack.append((lbl_start, lbl_end, lbl_update))

        # index = 0
        t_index = self.tm.new_temp()
        self.emit("copy", 0, None, t_index)

        # length = array_length(collection)
        t_len = self.tm.new_temp()
        self.emit("array_length", t_collection, None, t_len)

        self.emit("label", lbl_start, None, None)
        t_cond = self.tm.new_temp()
        self.emit("<", t_index, t_len, t_cond)
        self.emit("iffalse_goto", t_cond, None, lbl_end)

        # item = collection[index]
        t_item = self.tm.new_temp()
        self.emit("getidx", t_collection, t_index, t_item)

        # guardar en variable "name" (simplificamos como var local/global normal)
        self._store_var(node.name, t_item)

        # body
        self._visit_Block(node.body)

        # update: index++
        self.emit("label", lbl_update, None, None)
        t_one = self.tm.new_temp()
        self.emit("copy", 1, None, t_one)
        t_next = self.tm.new_temp()
        self.emit("+", t_index, t_one, t_next)
        self.emit("copy", t_next, None, t_index)

        self.emit("goto", None, None, lbl_start)
        self.emit("label", lbl_end, None, None)

        self.tm.release_ref(t_collection)
        self.loop_stack.pop()

    def _visit_TryCatch(self, node: TryCatch):
        """
        Implementación simplificada usando runtime de excepciones:
        push_handler(catch_label)
        try_block
        pop_handler
        goto end
        catch_label:
            get_exception -> temp
            store en var
            catch_block
        end:
        """
        lbl_catch = self.tm.newLabel()
        lbl_end = self.tm.newLabel()

        # push handler
        self.emit("push_handler", lbl_catch, None, None)

        # try
        self._visit_Block(node.try_block)

        # si termina sin lanzar, pop handler
        self.emit("pop_handler", None, None, None)
        self.emit("goto", None, None, lbl_end)

        # catch
        self.emit("label", lbl_catch, None, None)
        t_exc = self.tm.new_temp()
        self.emit("get_exception", None, None, t_exc)
        self._store_var(node.var, t_exc)

        self._visit_Block(node.catch_block)

        self.emit("label", lbl_end, None, None)

    def _visit_Switch(self, node: Switch):
        # switch(expr) { cases... default... }
        t_scrut = self._visit(node.expr)
        self.tm.add_ref(t_scrut)
        lbl_end = self.tm.newLabel()

        case_labels = [self.tm.newLabel() for _ in node.cases]
        default_label = self.tm.newLabel() if node.default else lbl_end

        # Comparaciones para cada case
        for (c, lbl_case) in zip(node.cases, case_labels):
            t_case_val = self._visit(c.expr)
            t_cmp = self.tm.new_temp()
            self.emit("==", t_scrut, t_case_val, t_cmp)
            self.emit("iftrue_goto", t_cmp, None, lbl_case)

        # default
        if node.default:
            self.emit("goto", None, None, default_label)
        else:
            self.emit("goto", None, None, lbl_end)

        # cuerpos de cases
        for (c, lbl_case) in zip(node.cases, case_labels):
            self.emit("label", lbl_case, None, None)
            for s in c.statements:
                self._visit(s)

        if node.default:
            self.emit("label", default_label, None, None)
            for s in node.default:
                self._visit(s)

        self.emit("label", lbl_end, None, None)
        self.tm.release_ref(t_scrut)

    def _visit_Return(self, node: Return):
        if node.expr is None:
            self.emit("ret", None, None, None)
        else:
            t_val = self._visit(node.expr)
            self.tm.add_ref(t_val)
            self.emit("ret", t_val, None, None)
            self.tm.release_ref(t_val)

    def _visit_Break(self, node: Break):
        if not self.loop_stack:
            # semantic ya lo validó; aquí sólo protegemos
            return
        _, lbl_end, _ = self.loop_stack[-1]
        self.emit("goto", None, None, lbl_end)

    def _visit_Continue(self, node: Continue):
        if not self.loop_stack:
            return
        _, _, lbl_update = self.loop_stack[-1]
        if lbl_update is None:
            return
        self.emit("goto", None, None, lbl_update)

    # ==================== expresiones ====================

    def _visit_IntLiteral(self, node: IntLiteral) -> str:
        t = self.tm.new_temp()
        self.emit("copy", node.value, None, t)
        return t

    def _visit_FloatLiteral(self, node: FloatLiteral) -> str:
        t = self.tm.new_temp()
        self.emit("copy", node.value, None, t)
        return t

    def _visit_StringLiteral(self, node: StringLiteral) -> str:
        # en el parse-tree usabas ctx.getText(), que incluía comillas.
        # Aquí las volvemos a agregar.
        text = '"' + node.value.replace('"', '\\"') + '"'
        t = self.tm.new_temp()
        self.emit("copy", text, None, t)
        return t

    def _visit_BooleanLiteral(self, node: BooleanLiteral) -> str:
        val = "true" if node.value else "false"
        t = self.tm.new_temp()
        self.emit("copy", val, None, t)
        return t

    def _visit_NullLiteral(self, node: NullLiteral) -> str:
        # representamos null como 0
        t = self.tm.new_temp()
        self.emit("copy", 0, None, t)
        return t

    def _visit_ListLiteral(self, node: ListLiteral) -> str:
        """
        Genera:
            alloc_array N, t_arr
            setidx t_arr, i, elem...
        """
        size = len(node.elements)
        t_arr = self.tm.new_temp()
        self.emit("alloc_array", size, None, t_arr)

        for i, e in enumerate(node.elements):
            t_elem = self._visit(e)
            self.tm.add_ref(t_elem)
            self.emit("setidx", t_arr, i, t_elem)
            self.tm.release_ref(t_elem)

        return t_arr

    def _visit_Var(self, node: Var) -> str:
        return self._load_var(node.name)

    def _visit_UnOp(self, node: UnOp) -> str:
        t_expr = self._visit(node.expr)
        self.tm.add_ref(t_expr)
        t_res = self.tm.new_temp()

        if node.op == "!":
            self.emit("not", t_expr, None, t_res)
        elif node.op == "+":
            # +x → x
            self.emit("copy", t_expr, None, t_res)
        elif node.op == "-":
            # -x → 0 - x
            t_zero = self.tm.new_temp()
            self.emit("copy", 0, None, t_zero)
            self.emit("-", t_zero, t_expr, t_res)
        else:
            # fallback: sólo copia
            self.emit("copy", t_expr, None, t_res)

        self.tm.release_ref(t_expr)
        return t_res

    def _visit_BinOp(self, node: BinOp) -> str:
        t_left = self._visit(node.left)
        t_right = self._visit(node.right)
        self.tm.add_ref(t_left)
        self.tm.add_ref(t_right)

        t_res = self.tm.new_temp()
        self.emit(node.op, t_left, t_right, t_res)

        self.tm.release_ref(t_left)
        self.tm.release_ref(t_right)
        return t_res

    def _visit_Ternary(self, node: Ternary) -> str:
        t_cond = self._visit(node.condition)
        self.tm.add_ref(t_cond)

        lbl_true = self.tm.newLabel()
        lbl_false = self.tm.newLabel()
        lbl_end = self.tm.newLabel()
        t_res = self.tm.new_temp()

        self.emit("iftrue_goto", t_cond, None, lbl_true)
        self.emit("goto", None, None, lbl_false)
        self.tm.release_ref(t_cond)

        # false
        self.emit("label", lbl_false, None, None)
        t_f = self._visit(node.else_branch)
        self.tm.add_ref(t_f)
        self.emit("copy", t_f, None, t_res)
        self.tm.release_ref(t_f)
        self.emit("goto", None, None, lbl_end)

        # true
        self.emit("label", lbl_true, None, None)
        t_t = self._visit(node.then_branch)
        self.tm.add_ref(t_t)
        self.emit("copy", t_t, None, t_res)
        self.tm.release_ref(t_t)

        self.emit("label", lbl_end, None, None)
        return t_res

    def _visit_Member(self, node: Member) -> str:
        t_obj = self._visit(node.object)
        self.tm.add_ref(t_obj)
        t_res = self.tm.new_temp()
        self.emit("getprop", t_obj, node.name, t_res)
        self.tm.release_ref(t_obj)
        return t_res

    def _visit_Index(self, node: Index) -> str:
        t_seq = self._visit(node.seq)
        t_idx = self._visit(node.index)
        self.tm.add_ref(t_seq)
        self.tm.add_ref(t_idx)

        t_res = self.tm.new_temp()
        self.emit("getidx", t_seq, t_idx, t_res)

        self.tm.release_ref(t_seq)
        self.tm.release_ref(t_idx)
        return t_res

    def _visit_Call(self, node: Call) -> str:
        """
        Llamada a función:
          - callee puede ser Var (función) o Member (método).
        Convención:
          emit("param", arg, None, None) para cada argumento
          emit("call", label_o_temp, argc, t_res)
        """
        # 1) evaluar argumentos
        arg_temps: list[str] = []
        for a in node.args:
            t_a = self._visit(a)
            self.tm.add_ref(t_a)
            arg_temps.append(t_a)

        # 2) determinar el "destino" de la llamada
        #    - función normal: label por nombre
        #    - método: label "Clase.metodo" (ya lo resolvió el SemanticAnalyzer en FunctionSymbol)
        callee = node.callee
        label_or_temp = None

        if isinstance(callee, Var):
            # buscar FunctionSymbol
            f_sym = self._current_func_symbol(callee.name)
            if f_sym:
                label_or_temp = f_sym.label or f_sym.name
            else:
                # fallback: nombre directo
                label_or_temp = callee.name

        elif isinstance(callee, Member):
            # método: obj.m(...)
            # evaluamos el objeto para 'this'
            t_obj = self._visit(callee.object)
            self.tm.add_ref(t_obj)

            # asumimos label "Clase.metodo" ya conocido por SemanticAnalyzer,
            # pero aquí no tenemos el tipo estático. Hacemos fallback:
            label_or_temp = callee.name   # runtime usará dynamic dispatch si lo tienes

            # Si quisieras pasar 'this' explícito como primer param, podrías:
            # self.emit("param", t_obj, None, None)
            # y aumentar argc en 1. De momento no, porque tu convención
            # de runtime/métodos lo maneja distinto (cs_alloc_object/cs_getprop).
            self.tm.release_ref(t_obj)

        else:
            # callee genérico: evaluar y usar indirecto
            t_fun = self._visit(callee)
            self.tm.add_ref(t_fun)
            label_or_temp = t_fun   # llamada indirecta
            # y no liberamos t_fun hasta después

        # 3) emitir params
        for t_a in arg_temps:
            self.emit("param", t_a, None, None)
            self.tm.release_ref(t_a)

        # 4) llamada
        t_res = self.tm.new_temp()
        self.emit("call", label_or_temp, len(node.args), t_res)

        return t_res

    def _visit_New(self, node: New) -> str:
        """
        new Clase(args)
        Usamos un runtime cs_alloc_object + llamada opcional a constructor.
        Aquí emitimos un IR genérico:
            alloc_object Clase, t_obj
            param t_obj (opcional, si el ctor recibe this)
            param args...
            call Clase.constructor, argc, t_tmp
        Pero para simplificar usamos una sola instrucción 'newobj'.
        """
        # Evaluar args
        arg_temps = []
        for a in node.args:
            t_a = self._visit(a)
            self.tm.add_ref(t_a)
            arg_temps.append(t_a)

        t_obj = self.tm.new_temp()
        self.emit("newobj", node.class_name, len(node.args), t_obj)

        for t_a in arg_temps:
            self.tm.release_ref(t_a)

        return t_obj

    def _visit_This(self, node: This) -> str:
        """
        this → asumimos que el runtime tiene 'this' en algún registro / FP offset.
        Aquí podríamos modelarlo como 'load FP[8]' pero para no acoplar,
        lo representamos como una pseudo-variable 'this'.
        """
        return self._load_var("this")
