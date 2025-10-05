"""
code generator que es visitor del AST 

temporales: t1, t2...
etiquetas: L1, L2 ...
devuelve el temp donde quedo el valor de cada expresion
asume que el semantic analyzer ya valido tipos/herencia

"""
from typing import Optional, List
from IR import Instr, make

class CodeGen:
    def __init__(self, symtab):
        self.code: List[Instr] = []
        self.temp_id= 0 
        self.label_id=0
        self.symtab = symtab
        self.current_func: Optional[str] = None
        self.current_func_sym = None
        self.current_class: Optional[str] = None
        self.loop_stack = [] #cada item (Lcond, Lend, Lcontinue)
        # nombres de registros para el backend
        self.FP = "FP"
        self.GP = "GP"

    # helpers

    def new_temp(self) -> str:
        self.temp_id +=1
        return f"t{self.temp_id}"
    
    def new_label(self, base: str = "L")->str:
        self.label_id +=1
        return f"{base}{self.label_id}"
    
    def emit(self, *args) ->None:
        self.code.append(make(*args))

    def generate(self, ast) -> List[Instr]:
        self.visit(ast)
        return self.code
    
    def _funcsym(self):
        return self.current_func_sym
        # obtiene el FunctionSymbol actual

    def _addr_of_var(self, name: str):
        """
        Devuelve dirección lógica de 'name' como (base, offset, kind):
        kind ∈ {"local","param","global"}
        """
        f = self._funcsym()
        if f:
            if name in (f.local_offsets or {}):
                return (self.FP, f.local_offsets[name], "local")
            if name in (f.param_offsets or {}):
                return (self.FP, f.param_offsets[name], "param")
        # global
        return (self.GP, name, "global")

    def _field_offset(self, obj_node, field_name: str) -> int:
        # inferir tipo del objeto desde symtab/clase actual
        # cuando el objeto es 'this':
        if obj_node.__class__.__name__ == "This" and self.current_class:
            T = self.symtab.types.get(self.current_class)
        else:
            # si es Var, el analizador tipó esa variable; puedes buscar su TypeSymbol en la tabla:
            T = None
            if obj_node.__class__.__name__ == "Var":
                sym = self.symtab.current_scope.resolve(obj_node.name) if self.symtab.current_scope else None
                T = getattr(sym, 'type', None)
        # fallback: por nombre calificado
        if not T and self.current_class:
            T = self.symtab.types.get(self.current_class)
        # lee _field_offsets
        offmap = getattr(T, "_field_offsets", {}) if T else {}
        return offmap.get(field_name, 0)


    # dispatcher - pasador

    def visit(self, node):
        if node is None: 
            return
        
        m= getattr(self, f"visit_{node.__class__.__name__}", None)
        if m:
            return m(node)

        # fallback que recorre posible .statements/.body
        for fld in ("statements", "body"):
            val = getattr(node, fld, None)
            if isinstance(val, list):
                for s in val:
                    self.visit(s)
            else:
                self.visit(val)
        return None
    
    # nodos raiz / statements
    def visit_Program(self, node):
        for s in node.statements: 
            self.visit(s)

    def visit_Block(self, node):
        for s in node.statements:
            self.visit(s)

    #declaraciones

    def visit_VarDecl(self, node):
        # si tiene init: traducirlo y hacer copy a la var
        if node.init:
            src = self.visit(node.init)
            #se asume que el nombre del simbolo es un destino valido
            if src is not None:
                self.emit('copy', node.name, src)
        #sino tiene init -> nada se puede inicializar por defecto

    def visit_Assign(self, node):
        rhs = self.visit(node.expr)

        #casos lvalue
        t = node.target.__class__.__name__
        if t== "Var":
            base, off, kind = self._addr_of_var(node.target.name)
            self.emit('store', base, off, rhs)
            return
        elif t == "Member":
            obj = self.visit(node.target.object)
            off = self._field_offset(node.target.object, node.target.name)
            self.emit('store', obj, str(off), rhs)
            return
        elif t == "Index":
            arr = self.visit(node.target.seq)
            idx = self.visit(node.target.index)
            self.emit('setidx', arr, idx, rhs)
        else:
            # fallback
            self.emit('copy', str(node.target), rhs)

    def visit_ExprStmt(self, node):
        self.visit(node.expr)

    def visit_PrintStmt(self, node):
        v = self.visit(node.expr)
        self.emit('param', v)
        self.emit('call', None, 'print', 1)
    
    #control de flujo p3
    def visit_If(self, node):
        cond = self.visit(node.condition)
        Lelse = self.new_label('Lelse')
        Lend = self.new_label('Lend')
        self.emit('iffalse_goto', cond, Lelse)
        self.visit(node.then_branch)
        self.emit('goto', Lend)
        self.emit('label', Lelse)
        if node.else_branch:
            self.visit(node.else_branch)
        self.emit('label', Lend)


    def visit_While(self, node):
        Lcond = self.new_label('Lcond')
        Lend  = self.new_label('Lend')
        self.loop_stack.append((Lcond, Lend, Lcond))
        self.emit('label', Lcond)
        cond = self.visit(node.condition)
        self.emit('iffalse_goto', cond, Lend)
        self.visit(node.body)
        self.emit('goto', Lcond)
        self.emit('label', Lend)
        self.loop_stack.pop()

    def visit_DoWhile(self, node):
        Lbody = self.new_label('Lbody')
        Lcond = self.new_label('Lcond')
        Lend  = self.new_label('Lend')
        self.loop_stack.append((Lcond, Lend, Lcond))
        self.emit('label', Lbody)
        self.visit(node.body)
        self.emit('label', Lcond)
        cond = self.visit(node.condition)
        self.emit('if_goto', cond, Lbody)
        self.emit('label', Lend)
        self.loop_stack.pop()

    def visit_For(self, node):
        if node.init: self.visit(node.init)
        Lcond = self.new_label('Lcond')
        Lstep = self.new_label('Lstep')
        Lend  = self.new_label('Lend')
        self.loop_stack.append((Lcond, Lend, Lstep))
        self.emit('label', Lcond)
        if node.condition:
            c = self.visit(node.condition)
            self.emit('iffalse_goto', c, Lend)
        self.visit(node.body)
        self.emit('label', Lstep)
        if node.step: self.visit(node.step)
        self.emit('goto', Lcond)
        self.emit('label', Lend)
        self.loop_stack.pop()

    def visit_Break(self, node):
        if self.loop_stack:
            _, Lend, _ = self.loop_stack[-1]
            self.emit('goto', Lend)

    def visit_Continue(self, node):
        if self.loop_stack:
            _, _, Lcont = self.loop_stack[-1]
            self.emit('goto', Lcont)

    def visit_Foreach(self, node):
        # asumimos 'iter' es lista y generamos index-based loop
        arr = self.visit(node.iterable)
        i   = self.new_temp()
        n   = self.new_temp()
        self.emit('copy', i, '0')
        self.emit('length', n, arr)

        Lcond = self.new_label('Lcond')
        Lstep = self.new_label('Lstep')
        Lend  = self.new_label('Lend')
        self.loop_stack.append((Lcond, Lend, Lstep))

        self.emit('label', Lcond)
        tcmp = self.new_temp()
        self.emit('lt', tcmp, i, n)            # tcmp = i < n
        self.emit('iffalse_goto', tcmp, Lend)

        # item = arr[i]
        tmp = self.new_temp()
        self.emit('getidx', tmp, arr, i)       # tmp = arr[i]
        self.emit('copy', node.name, tmp)      # bind variable foreach

        # body
        self.visit(node.body)

        # step
        self.emit('label', Lstep)
        t1 = self.new_temp()
        self.emit('add', t1, i, '1')
        self.emit('copy', i, t1)
        self.emit('goto', Lcond)

        self.emit('label', Lend)
        self.loop_stack.pop()


    def visit_TryCatch(self, node):
        # genera cuerpo; catch al parecer se puede modelar a alto nivel
        self.visit(node.try_block)
        self.visit(node.catch_block)

    def visit_Switch(self, node):
        # cascada de if/else
        scrut = self.visit(node.expr)
        Lend = self.new_label('Lsw_end')
        for case in node.cases:
            Lnext = self.new_label('Lnext')
            rhs = self.visit(case.expr)
            tcmp = self.new_temp()
            self.emit('eq', tcmp, scrut, rhs)
            self.emit('iffalse_goto', tcmp, Lnext)
            for s in case.statements:
                self.visit(s)
            self.emit('goto', Lend)
            self.emit('label', Lnext)
        # default
        for s in (node.default or []):
            self.visit(s)
        self.emit('label', Lend)

    def visit_Return(self, node):
        if node.expr:
            v = self.visit(node.expr)
            self.emit('ret', v)
        else:
            self.emit('ret_void')

    # expresiones
    def visit_IntLiteral(self, node):
        t = self.new_temp()
        self.emit('copy', t, str(node.value))
        return t

    def visit_FloatLiteral(self, node):
        t = self.new_temp()
        self.emit('copy', t, str(node.value))
        return t

    def visit_StringLiteral(self, node):
        t = self.new_temp()
        self.emit('copy', t, f'"{node.value}"')
        return t

    def visit_BooleanLiteral(self, node):
        t = self.new_temp()
        self.emit('copy', t, '1' if node.value else '0')
        return t

    def visit_NullLiteral(self, node):
        t = self.new_temp()
        self.emit('copy', t, 'null')
        return t

    def visit_ListLiteral(self, node):
        # newlist + setidx
        dst = self.new_temp()
        n = len(node.elements)
        self.emit('newlist', dst, str(n))
        for i, e in enumerate(node.elements):
            v = self.visit(e)
            self.emit('setidx', dst, str(i), v)
        return dst
    
    def visit_Var(self, node):
        base, off, kind = self._addr_of_var(node.name)
        t = self.new_temp()
        # si es global y el backend carga por etiqueta, usar (GP, etiqueta)
        self.emit('load', t, base, off)
        return t
    
    def visit_Member(self, node):
        base_obj = self.visit(node.object)  # temp con puntero/base del objeto
        off = self._field_offset(node.object, node.name)
        dst = self.new_temp()
        # asumimos que 'base_obj' es la dirección base del objeto
        self.emit('load', dst, base_obj, str(off))  # dst = *(base + off)
        return dst

    def visit_Index(self, node):
        arr = self.visit(node.seq)
        idx = self.visit(node.index)
        t = self.new_temp()
        self.emit('getidx', t, arr, idx)
        return t
    
    def visit_New(self, node):
        dst = self.new_temp()
        self.emit('new', dst, node.class_name)
        # llamada al constructor 
        if node.args:
            for a in node.args:
                self.emit('param', self.visit(a))
            self.emit('call', None, f'{node.class_name}.constructor', len(node.args))
        return dst
    
    def visit_This(self, node):
    # simbolo 'this' como fuente, lo copiamos a un temp
        t = self.new_temp()
        self.emit('copy', t, 'this')
        return t
    
    def visit_Call(self, node):
        # evalúa argumentos en orden y emite 'param'
        argvals = []

        for a in node.args:
            v = self.visit(a)
            self.emit('param', v)  # (op='param', a=v)
            argvals.append(v)
        for v in argvals:
            # AQUI DEBERIA DE IR EL RECICLAJE
            pass

        dst = self.new_temp()

        # dos formas: Var o Member
        if node.callee.__class__.__name__ == "Var":
            self.emit('call', dst, node.callee.name, len(node.args))
            return dst
        elif node.callee.__class__.__name__ == "Member":
            # método: pasar 'this' como primer parámetro
            obj = self.visit(node.callee.object)
            self.emit('param', obj)
            # a=dst, b=Clase.metodo (o calificador inferido), c=nargs
            self.emit('call', dst,
                    f"{self._infer_obj_name(node.callee.object)}.{node.callee.name}",
                    1 + len(node.args))
            return dst
        # fallback
        self.emit('call', dst, '<fun>', len(node.args))
        return dst

    def _infer_obj_name(self, obj_node) -> str:
        """
        Intenta devolver el nombre de tipo del objeto para calificar el método.
        - this -> la clase actual (si hay)
        - Var  -> consulta la tabla de símbolos y devuelve el tipo (si está disponible)

        """
        # this -> clase actual
        if obj_node.__class__.__name__ == "This" and self.current_class:
            return self.current_class

        # Var -> mira tipo en la symtab si existe
        if obj_node.__class__.__name__ == "Var":
            try:
                sym = self.symtab.current_scope.resolve(obj_node.name)
                if sym and getattr(sym, 'type', None):
                    # TypeSymbol.name (ej. "Dog")
                    return sym.type.name
            except Exception:
                pass

        # fallback (desconocido)
        return "obj"

    def visit_BinOp(self, node):

        if node.op == '&&':
            return self._gen_logical_and(node.left, node.right)
        if node.op == '||':
            return self._gen_logical_or(node.left, node.right)
        
        opmap = {
            '+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'mod',
            '==': 'eq', '!=': 'ne', '<': 'lt', '<=': 'le', '>': 'gt', '>=': 'ge',
            '&&': 'and', '||': 'or'
        }
        a = self.visit(node.left)
        b = self.visit(node.right)
        dst = self.new_temp()
        self.emit(opmap[node.op], dst, a, b)   # a=dst, b=lhs, c=rhs
        return dst
    
    def _gen_logical_and(self, left, right):
        # t = 0; if !left goto Lend; t = right; Lend:
        t    = self.new_temp()
        Lend = self.new_label('Land_end')
        self.emit('copy', t, '0')
        a = self.visit(left)
        self.emit('iffalse_goto', a, Lend)
        b = self.visit(right)
        self.emit('copy', t, b)
        self.emit('label', Lend)
        return t

    def _gen_logical_or(self, left, right):
        # t = 1; if left goto Lend; t = right; Lend:
        t    = self.new_temp()
        Lend = self.new_label('Lor_end')
        self.emit('copy', t, '1')
        a = self.visit(left)
        self.emit('if_goto', a, Lend)   # si tiene solo 'iffalse_goto', usa eq/!eq
        b = self.visit(right)
        self.emit('copy', t, b)
        self.emit('label', Lend)
        return t
    
    def visit_UnOp(self, node):
        x = self.visit(node.expr)
        dst = self.new_temp()
        if node.op == '!':
            # not x -> eq dst, x, 0 
            self.emit('eq', dst, x, '0')
        elif node.op == '+':
            self.emit('copy', dst, x)
        elif node.op == '-':
            zero = self.new_temp()
            self.emit('copy', zero, '0')
            self.emit('sub', dst, zero, x)
        else:
            self.emit('copy', dst, x)
        return dst
    
    def visit_Ternary(self, node):
        cond = self.visit(node.condition)
        Lelse = self.new_label('Lelse')
        Lend  = self.new_label('Lend')
        dst   = self.new_temp()
        self.emit('iffalse_goto', cond, Lelse)
        v1 = self.visit(node.then_branch)
        self.emit('copy', dst, v1)
        self.emit('goto', Lend)
        self.emit('label', Lelse)
        v2 = self.visit(node.else_branch)
        self.emit('copy', dst, v2)
        self.emit('label', Lend)
        return dst
    
    #  util fake para foreach  es solo helper
    def visit_IntLiteral_fake(self, temp_with_value) -> str:
        # devolvemos el temp directamente
        return temp_with_value

    def visit_Index_fake(self, arr_temp, idx_temp) -> str:
        t = self.new_temp()
        self.emit('getidx', t, arr_temp, idx_temp)
        return t
    
    # funciones y clases
    def visit_FuncDecl(self, node):
        """
        Emite un bloque por función en el IR:
            func <nombre>
            ...cuerpo...
            endfunc  # <nombre>
        """
        fname = node.name if not self.current_class else f"{self.current_class}.{node.name}"
        # busca FunctionSymbol con ese nombre calificado
        f = self.symtab.global_scope.resolve(fname)
        if not f:
            # intenta sin calificar si es top-level
            f = self.symtab.global_scope.resolve(node.name)

        self.emit('func', fname)
        prev_func = self.current_func
        prev_sym  = self.current_func_sym
        self.current_func = fname
        self.current_func_sym = f

        # prologo: enter con frame size
        framesz = getattr(f, 'frame_size', 0) or 0
        self.emit('enter', framesz)

        try:
            # Los parámetros en  AST ya son variables visibles en el cuerpo,
            # así que no hace falta generar nada especial aquí.
            # Visita el cuerpo (Block)
            self.visit(node.body)
        finally:
            # epilogo
            self.emit('leave')
            self.current_func = prev_func
            self.current_func_sym = prev_sym
            # marca fin
            self.emit('endfunc', fname)


    


    def visit_ClassDecl(self, node):
        """
        Visita propiedades (no generan código) y métodos.
        Los métodos se emiten como funciones calificadas: Clase.metodo
        """
        prev_cls = self.current_class
        self.current_class = node.name
        try:
            #inicio de la clase
            self.emit('class', node.name)
            # propiedades: no generan TAC (solo layout)
            for p in getattr(node, "properties", []):
                pass
            # métodos
            for m in getattr(node, "methods", []):
                self.visit(m)  # esto llama a visit_FuncDecl y emitirá 'Clase.metodo'
            # fin de la clase
            self.emit('endclass', node.name)
        finally:
            self.current_class = prev_cls
