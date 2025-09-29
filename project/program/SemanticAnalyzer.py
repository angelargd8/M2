"""
Implementa el analizador semántico para el lenguaje de Compiscript su función es verificar que el programa sea correcto a nivel de tipos, ámbitos, herencia y reglas semánticas.  
Los métodos de utilidades son para agregar errores, verificar tipos, herencia y propiedades 
Tiene dos pasadas principales: 

- Collect_signatures: que recolecta firmas de funciones, métodos y clases y construye la información de herencia y propiedades 
- Check: recorre el AST y válida las reglas semánticas (como tipos, inicialización...)  

Los métodos _visit_ para cada tipo del nodo de AST realiza las validaciones correspondientes, como declaraciones, asignaciones, control de flujo, expresiones.  
Y reporta errores semánticos con información de la línea y columna. 
"""
from typing import List, Optional, Any, Dict
from SymbolTable import SymbolTable, Scope, VariableSymbol, FunctionSymbol, TypeSymbol


# crea el analizador con la tabla de simbolos 
class SemanticAnalyzer:
    def __init__(self, symtab: Optional[SymbolTable] = None):

        self.symtab = symtab or SymbolTable()
        self.errors: List[str] = []
        self._func_ret_stack: List[TypeSymbol] = []
        self._class_stack: List[str] = []

        # soporte adicional
        self.loop_depth: int = 0
        # props por clase: { "Clase": { "prop": TypeSymbol, ... } }
        self.class_props: Dict[str, Dict[str, TypeSymbol]] = {}
        # herencia: { "Clase": "Base" }
        self.class_base: Dict[str, Optional[str]] = {}

        if "list" not in self.symtab.types:
            self.symtab.types["list"] = TypeSymbol("list")

    # ---------------------------- utilidades ----------------------------
    
    #agrega un error con [line:col]
    def error(self, msg: str, node: Optional[Any] = None):
        line = getattr(node, "line", None)
        col = getattr(node, "col", None)
        if line is not None and col is not None:
            self.errors.append(f"[{line}:{col}] {msg}")
        else:
            self.errors.append(msg)

    # helper para saber si una funcion tiene cuerpo
    def _func_has_body(self, func_node) -> bool:
        body = getattr(func_node, "body", None)
        if body is None:
            return False
        if body.__class__.__name__ == "Block":
            return True
        if isinstance(body, list):
            return len(body) > 0
        return True

    # verifica que la condicion se abool en el if/while/do/for
    def _expect_bool(self, expr, where: str):
        t = self._infer_expr_type(expr)
        if t and t.name != "bool":
            self.error(f"Condición en {where} debe ser bool, es {t.name}.", expr)

    # ---- helpers de tipos/listas ----

    #int o float
    def _is_numeric(self, t: Optional[TypeSymbol]) -> bool:
        return bool(t) and t.name in ("int", "float")

    # unifica tipos para literales de lista 
    def _unify_types(self, a: Optional[TypeSymbol], b: Optional[TypeSymbol]) -> Optional[TypeSymbol]:
        """Unifica tipos para literales de lista (admite promoción int->float y listas anidadas)."""
        if a is None: return b
        if b is None: return a
        if a == b:    return a

        # Promoción numérica
        if self._is_numeric(a) and self._is_numeric(b):
            return self.symtab.types["float"]

        # Listas anidadas: list<X> con list<Y> -> list<unify(X,Y)>
        if a.name == "list" and b.name == "list":
            u = self._unify_types(a.elem, b.elem)
            return TypeSymbol("list", elem=u) if u else None

        # no unificables
        return None

    # ---- helpers de herencia ----

    # busca el tipo de propiedad hacia arriba en la cadena de herencia
    def _lookup_prop_type(self, cname: Optional[str], prop: str) -> Optional[TypeSymbol]:
        while cname:
            props = self.class_props.get(cname)
            if props and prop in props:
                return props[prop]
            cname = self.class_base.get(cname)
        return None

    # busca un metodo por herencia
    def _resolve_method(self, cname: Optional[str], method: str) -> Optional[FunctionSymbol]:
        while cname:
            qname = f"{cname}.{method}"
            f = self.symtab.global_scope.resolve(qname)
            if isinstance(f, FunctionSymbol):
                return f
            cname = self.class_base.get(cname)
        return None

    # busca el constructor por herencia
    def _resolve_ctor(self, cname: Optional[str]) -> Optional[FunctionSymbol]:
        return self._resolve_method(cname, "constructor")

    # --------------------- pasada 1: recolectar firmas ------------------
    # registra firmas de funciones top-level y metodos de clases y recoge propiedades de herencia
    
    # colecta firmas
    def collect_signatures(self, ast: Any):
        for stmt in getattr(ast, "statements", []):
            cname = stmt.__class__.__name__
            if cname == "FuncDecl":
                # top-level
                self._collect_func_signature(stmt)
            elif cname == "ClassDecl":
                self._collect_class_signatures(stmt)

    #colecta firmas de clase
    # registra: class_base[clase] =base
    # propiedades (heredadas + propias ) en class_prop
    # firmas de metodos como Clase.metodo en global
    def _collect_class_signatures(self, class_node):
        cname = class_node.name
        base = getattr(class_node, "base", None)
        self.class_base[cname] = base

        # registrar el tipo de clase
        if cname not in self.symtab.types:
            self.symtab.types[cname] = TypeSymbol(cname)

        # heredar props de base
        props: Dict[str, TypeSymbol] = {}
        if base and base in self.class_props:
            props.update(self.class_props[base])

        # props propias
        for p in getattr(class_node, "properties", []):
            try:
                pt = self.symtab.get_type(p.type or "void")
            except Exception as e:
                self.error(str(e), p)
                pt = self.symtab.types["void"]
            if p.name in props:
                self.error(f"Propiedad duplicada '{p.name}' en clase '{cname}'", p)
            props[p.name] = pt
        self.class_props[cname] = props

        # métodos (nombre calificado)
        for m in getattr(class_node, "methods", []):
            if m.__class__.__name__ != "FuncDecl":
                continue
            qualified = f"{cname}.{m.name}"
            self._define_function_signatures_global(qualified, m.params, m.return_type, m)

    # registra firma de funcion top-level en el global
    def _collect_func_signature(self, func_node):
        self._define_function_signatures_global(func_node.name, func_node.params, func_node.return_type, func_node)

    # ---- define firma (global) ----
    # define/acrualiza firma global, chequea compatibilidad y redefinicion
    def _define_function_signatures_global(self, name: str, params: List[Any], return_type_txt: Optional[str], node: Any):
        ret_t = self._safe_get_type(return_type_txt or "void", node)
        params_syms = self._build_params(params, node)

        existing = self.symtab.global_scope.resolve(name)
        if existing:
            if not isinstance(existing, FunctionSymbol):
                self.error(f"'{name}' ya fue declarable como variable/tipo. ", node)
                return
            if len(existing.params) != len(params_syms) or existing.return_type != ret_t:
                self.error(f"firma incompatible para funcion '{name}'.", node)
                return
            has_body = self._func_has_body(node)
            if existing.is_defined and has_body:
                self.error(f"redefinicion de funcion: '{name}' ", node)
            if has_body:
                existing.is_defined = True
                existing.decl_node = node
            return

        f = FunctionSymbol(
            name=name, params=params_syms, return_type=ret_t,
            is_defined=self._func_has_body(node), decl_node=node,
        )
        # GLOBAL: define en global
        self.symtab.global_scope.define(f)

    # ---- define firma (local/closure) ----
    # hoisting local, define funcion en el scope actual para funciones anidadas / clousures
    def _define_function_signatures_local(self, name: str, params: List[Any], return_type_txt: Optional[str], node: Any):
        ret_t = self._safe_get_type(return_type_txt or "void", node)
        params_syms = self._build_params(params, node)

        # redeclaración en scope actual
        if name in self.symtab.current_scope.symbols:
            self.error(f"Redeclaracion de función '{name}' en el mismo alcance.", node)
            return
        f = FunctionSymbol(
            name=name, params=params_syms, return_type=ret_t,
            is_defined=self._func_has_body(node), decl_node=node,
        )
        self.symtab.define_function(f)

    # seguro para obtener un tipo, reporta error si no existe
    def _safe_get_type(self, name: str, node: Any) -> TypeSymbol:
        try:
            return self.symtab.get_type(name)
        except Exception as e:
            self.error(str(e), node)
            return self.symtab.types["void"]

    # construye la lista de parámetros para una función
    # digamos convierte los params del AST a simbolos 
    # y chequea duplicados
    def _build_params(self, params: List[Any], node: Any) -> List[VariableSymbol]:
        params_syms: List[VariableSymbol] = []
        seen = set()
        for p in params or []:
            if p.name in seen:
                self.error(f"Parametro suplicado '{p.name}' en funcion.", node)
                continue
            seen.add(p.name)
            p_t = self._safe_get_type(p.type or "void", p)
            ps = VariableSymbol(name=p.name, type=p_t, const=False, initialized=True, decl_node=p)
            params_syms.append(ps)
        return params_syms

    # -------------------- pasada 2: chequeo semántico -------------------

    def check(self, ast: Any) -> List[str]:
        self._visit(ast)
        return self.errors

    # --------------------------- dispatcher -----------------------------

    # llama a _visit_<TipoDeNodo> si existe, sino recorre campos comunes como el statement y body
    def _visit(self, node: Any):
        if node is None:
            return
        t = node.__class__.__name__
        m = getattr(self, f"_visit_{t}", None)
        if m:
            return m(node)
        for fld in ("statements", "body", "then_branch", "else_branch", "cases", "default"):
            val = getattr(node, fld, None)
            if isinstance(val, list):
                for c in val:
                    self._visit(c)
            else:
                self._visit(val)

    # --------------------------- nodos raíz -----------------------------

    #recorre todas las sentencias
    def _visit_Program(self, node):
        for s in node.statements:
            self._visit(s)

    # crea scope de blocque, hoistea funciones locales
    # marca codigo muerto tras return/break/continue
    # visita sentencias
    def _visit_Block(self, node):
        self.symtab.push_scope("block")
        try:
            # Hoisting de funciones locales (para closures y llamadas antes de declarar)
            for s in node.statements:
                if s.__class__.__name__ == "FuncDecl":
                    self._define_function_signatures_local(s.name, s.params, s.return_type, s)

            terminated = False
            for s in node.statements:
                if terminated:
                    self.error("Código inalcanzable después de return/break/continue.", s)
                self._visit(s)
                if s.__class__.__name__ in ("Return", "Break", "Continue"):
                    terminated = True
        finally:
            self.symtab.pop_scope()

    # ------------------------ declaraciones/func ------------------------

    #declara variable
    #tipo declarado o inferido del inicializador
    # const requiere de inicializador
    # no redeclaracion en el mismo scope
    # chequea compatibilidad con el init, permite que init -> float cuando el destino es float
    def _visit_VarDecl(self, node):
        vtype: Optional[TypeSymbol] = None
        if node.type:
            vtype = self._safe_get_type(node.type, node)

        if node.name in self.symtab.current_scope.symbols:
            self.error(f"Redeclaracion de '{node.name}' en el mismo alcance.", node)
            return

        init_type = None
        if node.init is not None:
            init_type = self._infer_expr_type(node.init)

        if node.is_const and node.init is None:
            self.error(f"Constante '{node.name}' debe inicializarse en su declaración.", node)

        if vtype is None:
            if init_type is not None:
                vtype = init_type
            else:
                self.error(f"La variable '{node.name}' no tiene tipo ni inicializador ", node)
                vtype = self.symtab.types.get("void")

        if vtype and init_type and vtype != init_type:
            self.error(
                f"Tipo incompatible al inicializar '{node.name}': se esperaba {vtype}, obtuviste {init_type}.",
                node,
            )

        sym = VariableSymbol(
            name=node.name,
            type=vtype or self.symtab.types.get("void"),
            const=bool(node.is_const),
            initialized=node.init is not None,
            decl_node=node,
        )
        self.symtab.define_variable(sym)

    # entra al scope de la funcion
    # inyecta parametros
    # apila tipo de retorno esperado
    # visita el cuerpo y permite funciones anidadas/clousures
    def _visit_FuncDecl(self, node):
        # nombre calificado si se trata de método de clase
        qualname = f"{self._class_stack[-1]}.{node.name}" if self._class_stack else node.name

        # resolver desde el scope actual (permite funciones locales) y global si aplica
        f = self.symtab.current_scope.resolve(node.name)
        if not isinstance(f, FunctionSymbol):
            # tal vez es método calificado en global
            f = self.symtab.global_scope.resolve(qualname)
            if not isinstance(f, FunctionSymbol):
                self.error(f"Función '{qualname}' no resolvible.", node)
                return

        self.symtab.push_scope(f"func {qualname}")
        try:
            for p in f.params:
                if p.name in self.symtab.current_scope.symbols:
                    self.error(f"Parametro duplicado '{p.name}' en '{qualname}'", node)
                else:
                    self.symtab.current_scope.define(p)
                    p.initialized = True

            self._func_ret_stack.append(f.return_type)
            body = node.body
            if body is None:
                return
            if body.__class__.__name__ == "Block":
                self._visit(body)
            elif isinstance(body, list):
                self.symtab.push_scope("func-body")
                try:
                    for s in body:
                        self._visit(s)
                finally:
                    self.symtab.pop_scope()
            else:
                self._visit(body)
        finally:
            self._func_ret_stack.pop()
            self.symtab.pop_scope()


    # entra al scope de clase y visita propiedades y metodos
    def _visit_ClassDecl(self, node):

        self._class_stack.append(node.name)
        self.symtab.push_scope(f"class {node.name}")
        try:
            for prop in getattr(node, "properties", []):
                self._visit(prop)
            for m in getattr(node, "methods", []):
                self._visit(m)
        finally:
            self.symtab.pop_scope()
            self._class_stack.pop()

    # ------------------------------ statements -------------------------------

    # asignaciones
    def _visit_Assign(self, node):
        target = node.target

        #valida la existencia por herencia y tipos, permite lo de int -> to float
        # obj.prop = expr
        if target.__class__.__name__ == "Member":
            obj_t = self._infer_expr_type(target.object)
            val_t = self._infer_expr_type(node.expr)
            cname = obj_t.name if obj_t else None
            prop_t = self._lookup_prop_type(cname, target.name) if cname else None
            if cname and prop_t is None:
                self.error(f"Propiedad '{target.name}' no existe en '{cname}'.", node)
            elif prop_t and val_t and prop_t != val_t:
                # permitir int -> float cuando prop es float
                if not (prop_t.name == "float" and val_t.name == "int"):
                    self.error(f"Asignación incompatible: '{target.name}' es {prop_t}, valor es {val_t}.", node)
            return

        # indice int, elemento compativle con elem si se conoce
        # a[i] = v;
        if target.__class__.__name__ == "Index":
            seq_t = self._infer_expr_type(target.seq)
            idx_t = self._infer_expr_type(target.index)
            if idx_t and idx_t.name != "int":
                self.error(f"Índice debe ser int, es {idx_t.name}.", target.index)
            val_t = self._infer_expr_type(node.expr)

            # si conocemos el tipo de elemento, validar
            if seq_t and seq_t.name == "list" and seq_t.elem:
                elem_t = seq_t.elem
                if val_t and elem_t != val_t:
                    # permitir int -> float cuando elem es float
                    if not (elem_t.name == "float" and val_t.name == "int"):
                        self.error(f"Asignación incompatible al elemento: se esperaba {elem_t}, obtuvo {val_t}.", node)
            return

        # asignación simple
        # variable existente, no reasignar const, tipos compatibles
        # x = expr;
        name = None
        if isinstance(target, str):
            name = target
        elif target.__class__.__name__ == "Var":
            name = target.name

        if name is not None:
            sym = self.symtab.current_scope.resolve(name)
            if sym is None or not isinstance(sym, VariableSymbol):
                self.error(f"Variable no declarada: '{name}'", node)
                return
            if sym.const and sym.initialized:
                self.error(f"No se puede reasignar const '{name}'.", node)

            val_t = self._infer_expr_type(node.expr)
            var_t = sym.type
            if val_t and var_t and val_t != var_t:
                if not (var_t.name == "float" and val_t.name == "int"):
                    self.error(f"Asignación incompatible: '{name}' es {var_t}, valor es {val_t}.", node)
            sym.initialized = True
            return

        # fallback
        self._visit(target)
        self._infer_expr_type(node.expr)

    # visita expresion para las validaciones
    def _visit_ExprStmt(self, node):
        self._infer_expr_type(node.expr)

    # visita el print statement para las validaciones
    def _visit_PrintStmt(self, node):
        self._infer_expr_type(node.expr)

    # visita el if statement para las validaciones
    # tiene la condicion bool
    def _visit_If(self, node):
        self._expect_bool(node.condition, "if")
        self._visit(node.then_branch)
        if node.else_branch:
            self._visit(node.else_branch)

    # visita el while statement para las validaciones
    # tiene la condicion bool
    def _visit_While(self, node):
        self._expect_bool(node.condition, "while")
        self.loop_depth += 1
        try:
            self._visit(node.body)
        finally:
            self.loop_depth -= 1

    # visita el do-while statement para las validaciones
    # tiene cuerpo en bucle y la condicion bool al final
    def _visit_DoWhile(self, node):
        self.loop_depth += 1
        try:
            self._visit(node.body)
        finally:
            self.loop_depth -= 1
        self._expect_bool(node.condition, "do-while")

    # visita el for statement para las validaciones
    # tiene scope propio 
    # init/cond/step 
    def _visit_For(self, node):
        self.symtab.push_scope("for")
        try:
            if node.init is not None:
                self._visit(node.init)
            if node.condition is not None:
                self._expect_bool(node.condition, "for")
            if node.step is not None:
                self._infer_expr_type(node.step)
            self.loop_depth += 1
            try:
                self._visit(node.body)
            finally:
                self.loop_depth -= 1
        finally:
            self.symtab.pop_scope()

    # visita el foreach statement para las validaciones
    # tiene scope propio
    # itera list<elem> y declara la variable de iteracion con tipo elem
    def _visit_Foreach(self, node):
        self.symtab.push_scope("foreach")
        try:
            it_t = self._infer_expr_type(node.iterable)
            # tipo del iterador: elem del iterable si es list<elem>, o int por defecto
            vtype = self.symtab.types.get("int")
            if it_t and it_t.name == "list" and it_t.elem:
                vtype = it_t.elem
            vs = VariableSymbol(name=node.name, type=vtype, initialized=True, decl_node=node)
            self.symtab.define_variable(vs)

            self.loop_depth += 1
            try:
                self._visit(node.body)
            finally:
                self.loop_depth -= 1
        finally:
            self.symtab.pop_scope()

    # visita el break statement para las validaciones
    def _visit_Break(self, node):
        if self.loop_depth <= 0:
            self.error("'break' solo puede usarse dentro de un bucle.", node)

    # visita el continue statement para las validaciones
    def _visit_Continue(self, node):
        if self.loop_depth <= 0:
            self.error("'continue' solo puede usarse dentro de un bucle.", node)


    # visita el trycatch para las validaciones
    # crea scope para catch y declara la variable de excepcion
    def _visit_TryCatch(self, node):
        self._visit(node.try_block)
        self.symtab.push_scope("catch")
        try:
            vs = VariableSymbol(name=node.var, type=self.symtab.types.get("string"), initialized=True, decl_node=node)
            self.symtab.define_variable(vs)
            self._visit(node.catch_block)
        finally:
            self.symtab.pop_scope()

    # valida que cada case tenga el mismo tipo que switch(expr), visita casos y default
    def _visit_Switch(self, node):
        scrut_t = self._infer_expr_type(node.expr)
        self.symtab.push_scope("switch")
        try:
            for c in node.cases:
                ct = self._infer_expr_type(c.expr)
                if scrut_t and ct and scrut_t != ct:
                    self.error(f"Tipo incompatible en case: se esperaba {scrut_t}, obtuvo {ct}.", c.expr)
                for s in c.statements:
                    self._visit(s)
            for s in node.default or []:
                self._visit(s)
        finally:
            self.symtab.pop_scope()

    # visita el return statement para las validaciones
    # solo en funcion, revisa el tipo de retorno
    def _visit_Return(self, node):

        if not self._func_ret_stack:
            self.error("'return' fuera de una función.", node)
            return
        expected = self._func_ret_stack[-1]

        if node.expr is None:
            if expected.name != "void":
                self.error(f"Se esperaba retornar {expected} pero se retornó vacío.", node)
            return
        actual = self._infer_expr_type(node.expr)

        if actual and expected and actual != expected:
            # permitir int -> float
            if not (expected.name == "float" and actual.name == "int"):
                self.error(f"Tipo de retorno incompatible: se esperaba {expected}, obtuvo {actual}.", node)

    # --------------------------- inferencia tipos ------------------------

    # infiere el tipo de una expresión
    def _infer_expr_type(self, node) -> Optional[TypeSymbol]:
        if node is None:
            return None

        tname = node.__class__.__name__

        # literales int/float/string/bool, null, list<elem> con homogeneidad
        if tname == "IntLiteral":
            return self.symtab.types["int"]
        if tname == "FloatLiteral":
            return self.symtab.types["float"]
        if tname == "StringLiteral":
            return self.symtab.types["string"]
        if tname == "BooleanLiteral":
            return self.symtab.types["bool"]
        if tname == "NullLiteral":
            return None
        if tname == "ListLiteral":
            elem_t: Optional[TypeSymbol] = None
            for e in node.elements:
                et = self._infer_expr_type(e)
                elem_t = self._unify_types(elem_t, et)
                if elem_t is None and et is not None:
                    # elementos incompatibles
                    self.error("Elementos de la lista con tipos incompatibles.", e)
                    # continúa para reportar más, pero mantén None
            return TypeSymbol("list", elem=elem_t)

        # variables
        # resuelve las variables en cadena de scopes
        if tname == "Var":
            sym = self.symtab.current_scope.resolve(node.name)
            if not sym or not isinstance(sym, VariableSymbol):
                self.error(f"Identificador no declarado: '{node.name}'", node)
                return None
            return sym.type

        # binarios
        if tname == "BinOp":
            lt = self._infer_expr_type(node.left)
            rt = self._infer_expr_type(node.right)
            op = node.op

            # + numérico (int/float) o concatena si alguno es string
            if op == "+":
                if (lt and lt.name == "string") or (rt and rt.name == "string"):
                    return self.symtab.types["string"]
                if self._is_numeric(lt) and self._is_numeric(rt):
                    return self.symtab.types["float"] if "float" in (lt.name, rt.name) else self.symtab.types["int"]
                self.error(f"Operador '+' requiere numéricos o string, obtuvo {lt} y {rt}.", node)
                return None

            # - * / % solo numéricos, promociona a float si aplica
            if op in ["-", "*", "/", "%"]:
                if self._is_numeric(lt) and self._is_numeric(rt):
                    return self.symtab.types["float"] if "float" in (lt.name, rt.name) else self.symtab.types["int"]
                self.error(f"Operador '{op}' requiere operandos numéricos, obtuvo {lt} y {rt}.", node)
                return None

            # && || ambos bools
            if op in ["&&", "||"]:
                if lt and lt.name != "bool":
                    self.error(f"Operador '{op}' requiere bool a la izquierda, es {lt.name}.", node)
                if rt and rt.name != "bool":
                    self.error(f"Operador '{op}' requiere bool a la derecha, es {rt.name}.", node)
                return self.symtab.types["bool"]

            # < <= > >= numericos -> bools
            if op in ["<", "<=", ">", ">="]:
                if self._is_numeric(lt) and self._is_numeric(rt):
                    return self.symtab.types["bool"]
                self.error(f"Operador '{op}' requiere operandos numéricos, obtuvo {lt} y {rt}.", node)
                return self.symtab.types["bool"]

            # == != mismos tipos o par numerico -> bool
            if op in ["==", "!="]:
                if lt and rt:
                    same = lt == rt
                    both_num = self._is_numeric(lt) and self._is_numeric(rt)
                    if same or both_num:
                        return self.symtab.types["bool"]
                self.error(f"Comparación '{op}' entre tipos incompatibles: {lt} y {rt}.", node)
                return self.symtab.types["bool"]

            return None

        # unarios
        # ! booleando y +/- numérico
        if tname == "UnOp":
            if node.op == "!":
                rt = self._infer_expr_type(node.expr)
                if rt and rt.name != "bool":
                    self.error(f"Operador '!' requiere bool, es {rt.name}.", node)
                return self.symtab.types["bool"]
            
            if node.op in ["+", "-"]:
                rt = self._infer_expr_type(node.expr)
                if self._is_numeric(rt):
                    return rt
                self.error(f"Operador '{node.op}' requiere operando numérico, es {rt}.", node)
                return None
            return self._infer_expr_type(node.expr)

        # ternario
        # unifica ramas, si ambos tipos som compatibles
        # sino retorna None
        if tname == "Ternary":
            self._infer_expr_type(node.condition)
            t1 = self._infer_expr_type(node.then_branch)
            t2 = self._infer_expr_type(node.else_branch)
            if t1 and t2 and t1 == t2:
                return t1
            return None

        # llamadas
        if tname == "Call":
            callee = node.callee

            # función (local o global)
            # valida numero y tipo de argumentos
            if callee.__class__.__name__ == "Var":
                f = self.symtab.current_scope.resolve(callee.name)  # <-- soporte funciones locales
                if not isinstance(f, FunctionSymbol):
                    # intenta global (por compatibilidad)
                    f = self.symtab.global_scope.resolve(callee.name)
                if isinstance(f, FunctionSymbol):
                    if len(node.args) != len(f.params):
                        self.error(
                            f"Número de argumentos inválido para '{callee.name}': "
                            f"se esperaban {len(f.params)}, hay {len(node.args)}.",
                            node,
                        )
                    for a, p in zip(node.args, f.params):
                        at = self._infer_expr_type(a)
                        if at and p.type and at != p.type:
                            # permitir int -> float
                            if not (p.type.name == "float" and at.name == "int"):
                                self.error(
                                    f"Tipo de argumento incompatible en '{callee.name}': "
                                    f"se esperaba {p.type}, obtuvo {at}.",
                                    a,
                                )
                    return f.return_type
                else:
                    self.error(f"Llamada a algo que no es función: '{callee.name}'", node)
                    for a in node.args:
                        self._infer_expr_type(a)
                    return None

            # método (con herencia)
            # idem validacion de argumentos
            if callee.__class__.__name__ == "Member":
                obj_t = self._infer_expr_type(callee.object)
                for a in node.args:
                    self._infer_expr_type(a)
                if obj_t:
                    f = self._resolve_method(obj_t.name, callee.name)

                    if isinstance(f, FunctionSymbol):
                        # Verifica la cantidad de argumentos
                        if len(node.args) != len(f.params):
                            self.error(
                                f"Número de argumentos inválido para '{obj_t.name}.{callee.name}': "
                                f"se esperaban {len(f.params)}, hay {len(node.args)}.",
                                node,
                            )
                        for a, p in zip(node.args, f.params):
                            at = self._infer_expr_type(a)
                            if at and p.type and at != p.type:
                                if not (p.type.name == "float" and at.name == "int"):
                                    self.error(
                                        f"Tipo de argumento incompatible en '{obj_t.name}.{callee.name}': "
                                        f"se esperaba {p.type}, obtuvo {at}.",
                                        a,
                                    )
                        return f.return_type
                    self.error(f"Método no resoluble: '{callee.name}' en tipo '{obj_t.name}'", node)
                else:
                    self.error(f"Método no resoluble: '{callee.name}' en tipo '?'", node)
                return None

            for a in node.args:
                self._infer_expr_type(a)
            return None

        # acceso a miembro: obj.prop (con herencia)
        # devuelve el tipo de la propiedad con herencia o reporta si no existe
        if tname == "Member":
            obj_t = self._infer_expr_type(node.object)
            cname = obj_t.name if obj_t else None
            prop_t = self._lookup_prop_type(cname, node.name) if cname else None
            if prop_t:
                return prop_t
            if cname:
                # si no es propiedad, podría ser método; el error definitivo se da si lo intentan llamar
                self.error(f"Propiedad '{node.name}' no existe en '{cname}'.", node)
            return None

        # indexación
        # a[i]: i debe ser int
        # devuelve el tipo de elemento si no se conoce
        if tname == "Index":
            seq_t = self._infer_expr_type(node.seq)
            idx_t = self._infer_expr_type(node.index)
            if idx_t and idx_t.name != "int":
                self.error(f"Índice debe ser int, es {idx_t.name}.", node.index)
            if seq_t and seq_t.name == "list":
                return seq_t.elem  # puede ser None si lista vacía o desconocida
            return None

        # new (hereda constructor)
        # new Clase(args)
        # valida constructor por cadena de herencia, tipos/aritdad
        # devuelve tipo clase
        if tname == "New":
            for a in node.args:
                self._infer_expr_type(a)
            t = self.symtab.types.get(node.class_name)
            if not t:
                self.error(f"Tipo '{node.class_name}' no definido.", node)
            ctor = self._resolve_ctor(node.class_name)
            if isinstance(ctor, FunctionSymbol):
                if len(node.args) != len(ctor.params):
                    self.error(
                        f"Número de argumentos inválido para constructor de '{node.class_name}': "
                        f"se esperaban {len(ctor.params)}, hay {len(node.args)}.",
                        node,
                    )
                for a, p in zip(node.args, ctor.params):
                    at = self._infer_expr_type(a)
                    if at and p.type and at != p.type:
                        if not (p.type.name == "float" and at.name == "int"):
                            self.error(
                                f"Tipo de argumento incompatible en constructor de '{node.class_name}': "
                                f"se esperaba {p.type}, obtuvo {at}.",
                                a,
                            )
            elif len(node.args) != 0:
                self.error(f"Constructor no resoluble para '{node.class_name}' con {len(node.args)} argumento(s).", node)
            return t

        # this
        # solo se puede usar dentro de clase
        # devuelve el tipo de la clase actual
        if tname == "This":
            if self._class_stack:
                cname = self._class_stack[-1]
                t = self.symtab.get_type(cname)
                if t:
                    return t
                self.error(f"Uso de 'this' en clase '{cname}' no definido.", node)
            self.error(f"Uso de 'this' fuera de una clase.", node)
            return None

        # contenedores con .expr
        if hasattr(node, "expr"):
            return self._infer_expr_type(node.expr)

        # fallback: visita campos comunes
        for fld in ("left", "right", "condition", "then_branch", "else_branch", "body"):
            val = getattr(node, fld, None)
            if val is not None:
                self._infer_expr_type(val)
        return None
