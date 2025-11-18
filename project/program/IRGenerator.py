from gen.CompiscriptVisitor import CompiscriptVisitor
from TempManager import TempManager
from IR import Instr
from SymbolTable import VariableSymbol, FunctionSymbol, TypeSymbol


class IRGenerator(CompiscriptVisitor):
    def __init__(self, symtab=None):
        self.quads = []
        self.tm = TempManager()
        self.symtab = symtab
        # Stack para manejar break/continue en loops anidados
        # cada entrada: (label_start, label_end, label_update)
        self.loop_stack = []
        # this actual (en métodos de clase)
        self.current_this = None
        # tracking de clases para generación de constructores
        self.current_class = None

    # --------------- utilidades básicas -----------------

    def emit(self, op, a=None, b=None, r=None):
        self.quads.append(Instr(op, a, b, r))

    def generate(self, tree):
        self.visit(tree)
        return self.quads

    # ¿es un temporal (t0, t1, ...)?
    def _is_temp_name(self, name: str) -> bool:
        return isinstance(name, str) and name.startswith("t")

    # resuelve un símbolo por nombre, si hay tabla
    def _resolve_sym(self, name):
        if not self.symtab:
            return None
        return self.symtab.resolve(name)

    # dirección en memoria para un VariableSymbol (stack / param / global)
    def _addr_for_symbol(self, sym: VariableSymbol, fallback_name: str):
        if isinstance(sym, VariableSymbol):
            if sym.storage in ("stack", "param"):
                # offset es índice lógico; el codegen MIPS lo convertirá a bytes
                return f"FP[{sym.offset}]"
            else:
                # global/estática
                return sym.name
        # si no es VariableSymbol, devolvemos el nombre "tal cual"
        return fallback_name

    # dirección para un identificador (puede ser atributo, local, global...)
    def _addr_for_identifier(self, name: str):
        sym = self._resolve_sym(name)

        # atributo de instancia (cuando current_this está activo)
        if (
            self.current_this
            and isinstance(sym, VariableSymbol)
            and getattr(sym, "is_attribute", False)
        ):
            # ahora usamos una instrucción IR dedicada
            return ("attribute", self.current_this, name)

        # variable local / parámetro / global
        return self._addr_for_symbol(sym, name)

    # --------------- raíz del programa ------------------

    def visitProgram(self, ctx):
        # Primero: generar funciones y clases (declaraciones)
        for st in ctx.statement():
            if st.functionDeclaration():
                self.visit(st.functionDeclaration())
            elif st.classDeclaration():
                self.visit(st.classDeclaration())

        # Segundo: generar el "main" con el código suelto
        self.emit("label", "main", None, None)
        for st in ctx.statement():
            # cualquier statement que NO sea declaración de función/clase
            if not st.functionDeclaration() and not st.classDeclaration():
                self.visit(st)

        # ret implícito al final del main
        self.emit("ret", "0", None, None)
        return self.quads

    # --------------- expresiones literales --------------

    # ================================
    # FIX DEFINITIVO PARA ARRAY LITERALES
    # ================================

    def visitLiteralExpr(self, ctx):
        """
        Detecta números, strings, booleanos, null y arrays literales.
        """
        # Si es arrayLiteral, delegar a visitArrayLiteral
        if ctx.arrayLiteral():
            return self.visit(ctx.arrayLiteral())

        value = ctx.getText()
        t = self.tm.new_temp()
        self.emit("copy", value, None, t)
        return t


    # ---------------------------------
    # NUEVO: manejo correcto de arrays
    # ---------------------------------

    def visitArrayLiteral(self, ctx):
        """
        arrayLiteral : '[' (expression (',' expression)*)? ']'
        """
        # Lista de expresiones ANTLR reales
        exprs = ctx.expression()

        size = len(exprs)
        t_arr = self.tm.new_temp()

        # alloc_array <size> → t_arr
        self.emit("alloc_array", size, None, t_arr)

        # inicializar cada elemento
        for i, e in enumerate(exprs):
            # evaluar con visit (NUNCA texto crudo)
            t_elem = self.visit(e)
            self.tm.add_ref(t_elem)

            # setidx arr, i, valorTemp
            self.emit("setidx", t_arr, i, t_elem)

            self.tm.release_ref(t_elem)

        return t_arr

    # --------------- identificadores --------------------

    def visitIdentifierExpr(self, ctx):
        name = ctx.getText()
        symbol = self._resolve_sym(name)

        # variable ⇒ cargar desde memoria
        if isinstance(symbol, VariableSymbol):
            addr_info = self._addr_for_identifier(name)
            t = self.tm.new_temp()
            
            # si es atributo de instancia
            if isinstance(addr_info, tuple) and addr_info[0] == "attribute":
                _, obj, prop = addr_info
                self.emit("getprop", obj, prop, t)
            else:
                self.emit("load", addr_info, None, t)
            
            return t

        # función ⇒ usamos label/nombre como valor "callable"
        if isinstance(symbol, FunctionSymbol):
            addr = symbol.label or symbol.name
            t = self.tm.new_temp()
            self.emit("copy", addr, None, t)
            return t

        # tipo ⇒ se trata como literal de tipo (por ahora solo nombre)
        if isinstance(symbol, TypeSymbol):
            t = self.tm.new_temp()
            self.emit("copy", symbol.name, None, t)
            return t

        # no resuelto ⇒ tratamos el texto como valor literal
        t = self.tm.new_temp()
        self.emit("copy", name, None, t)
        return t

    # --------------- expr aritméticas / lógicas ---------

    def visitAdditiveExpr(self, ctx):
        t1 = self.visit(ctx.multiplicativeExpr(0))
        for i in range(1, len(ctx.multiplicativeExpr())):
            t2 = self.visit(ctx.multiplicativeExpr(i))
            op = ctx.getChild(2 * i - 1).getText()  # '+' o '-'

            self.tm.add_ref(t1); self.tm.add_ref(t2)
            t3 = self.tm.new_temp()
            self.emit(op, t1, t2, t3)
            self.tm.release_ref(t1); self.tm.release_ref(t2)

            t1 = t3
        return t1

    def visitMultiplicativeExpr(self, ctx):
        t1 = self.visit(ctx.unaryExpr(0))
        for i in range(1, len(ctx.unaryExpr())):
            t2 = self.visit(ctx.unaryExpr(i))
            op = ctx.getChild(2 * i - 1).getText()  # '*', '/', '%'

            self.tm.add_ref(t1); self.tm.add_ref(t2)
            t3 = self.tm.new_temp()
            self.emit(op, t1, t2, t3)
            self.tm.release_ref(t1); self.tm.release_ref(t2)

            t1 = t3
        return t1

    def visitRelationalExpr(self, ctx):
        t1 = self.visit(ctx.additiveExpr(0))
        for i in range(1, len(ctx.additiveExpr())):
            t2 = self.visit(ctx.additiveExpr(i))
            op = ctx.getChild(2 * i - 1).getText()  # '<', '<=', '>', '>='

            self.tm.add_ref(t1); self.tm.add_ref(t2)
            t3 = self.tm.new_temp()
            self.emit(op, t1, t2, t3)
            self.tm.release_ref(t1); self.tm.release_ref(t2)

            t1 = t3
        return t1

    def visitEqualityExpr(self, ctx):
        t1 = self.visit(ctx.relationalExpr(0))
        for i in range(1, len(ctx.relationalExpr())):
            t2 = self.visit(ctx.relationalExpr(i))
            op = ctx.getChild(2 * i - 1).getText()  # '==', '!='

            self.tm.add_ref(t1); self.tm.add_ref(t2)
            t3 = self.tm.new_temp()
            self.emit(op, t1, t2, t3)
            self.tm.release_ref(t1); self.tm.release_ref(t2)

            t1 = t3
        return t1

    def visitLogicalAndExpr(self, ctx):
        t1 = self.visit(ctx.equalityExpr(0))
        for i in range(1, len(ctx.equalityExpr())):
            t2 = self.visit(ctx.equalityExpr(i))

            self.tm.add_ref(t1); self.tm.add_ref(t2)
            t3 = self.tm.new_temp()
            self.emit("&&", t1, t2, t3)
            self.tm.release_ref(t1); self.tm.release_ref(t2)

            t1 = t3
        return t1

    def visitLogicalOrExpr(self, ctx):
        t1 = self.visit(ctx.logicalAndExpr(0))
        for i in range(1, len(ctx.logicalAndExpr())):
            t2 = self.visit(ctx.logicalAndExpr(i))

            self.tm.add_ref(t1); self.tm.add_ref(t2)
            t3 = self.tm.new_temp()
            self.emit("||", t1, t2, t3)
            self.tm.release_ref(t1); self.tm.release_ref(t2)

            t1 = t3
        return t1

    # --------------- declaraciones / asignaciones -------

    def visitVariableDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        addr_info = self._addr_for_identifier(name)

        if ctx.initializer():
            t_expr = self.visit(ctx.initializer().expression())
            self.tm.add_ref(t_expr)
            
            # si es atributo de instancia
            if isinstance(addr_info, tuple) and addr_info[0] == "attribute":
                _, obj, prop = addr_info
                self.emit("setprop", obj, prop, t_expr)
            else:
                self.emit("store", t_expr, None, addr_info)
            
            self.tm.release_ref(t_expr)
        return None

    def visitConstantDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        addr_info = self._addr_for_identifier(name)

        t_expr = self.visit(ctx.expression())
        self.tm.add_ref(t_expr)
        
        # si es atributo de instancia
        if isinstance(addr_info, tuple) and addr_info[0] == "attribute":
            _, obj, prop = addr_info
            self.emit("setprop", obj, prop, t_expr)
        else:
            self.emit("store", t_expr, None, addr_info)
        
        self.tm.release_ref(t_expr)

        sym = self._resolve_sym(name)
        if isinstance(sym, VariableSymbol):
            sym.const = True
        return None

    def visitAssignment(self, ctx):
        """Maneja: 
        1. Identifier '=' expression ';'
        2. expression '.' Identifier '=' expression ';'
        """
        
        # Caso 1: Identifier '=' expression ';'
        if ctx.Identifier() and len(ctx.expression()) == 1:
            name = ctx.Identifier().getText()
            
            # verificar si es constante
            sym = self._resolve_sym(name)
            if isinstance(sym, VariableSymbol) and getattr(sym, "const", False):
                raise Exception(f"No se puede asignar a la constante '{name}'")
            
            t_expr = self.visit(ctx.expression(0))
            addr_info = self._addr_for_identifier(name)

            self.tm.add_ref(t_expr)
            
            # si es atributo de instancia
            if isinstance(addr_info, tuple) and addr_info[0] == "attribute":
                _, obj, prop = addr_info
                self.emit("setprop", obj, prop, t_expr)
            else:
                self.emit("store", t_expr, None, addr_info)
            
            self.tm.release_ref(t_expr)
            return None
        
        # Caso 2: expression '.' Identifier '=' expression ';'
        elif len(ctx.expression()) == 2:
            # obtener el objeto (primera expression)
            t_obj = self.visit(ctx.expression(0))
            self.tm.add_ref(t_obj)
            
            # obtener el nombre de la propiedad
            prop_name = ctx.Identifier().getText()
            
            # evaluar el valor a asignar (segunda expression)
            t_value = self.visit(ctx.expression(1))
            self.tm.add_ref(t_value)
            
            # emitir setprop
            self.emit("setprop", t_obj, prop_name, t_value)
            
            self.tm.release_ref(t_obj)
            self.tm.release_ref(t_value)
            
            return None
        
        else:
            raise Exception(f"Formato de asignación no reconocido: {ctx.getText()}")
    
    def visitAssignExpr(self, ctx):
        """Maneja: leftHandSide '=' assignmentExpr (expression-level)"""
        # obtener el lado izquierdo (puede ser x, arr[i], obj.prop, etc.)
        lhs_ctx = ctx.lhs
        
        # evaluar el lado derecho primero
        t_value = self.visit(ctx.assignmentExpr())
        self.tm.add_ref(t_value)
        
        # obtener la base del LHS
        base_text = lhs_ctx.primaryAtom().getText()
        sym = self._resolve_sym(base_text)
        
        # si no hay sufijos, es asignación simple a variable
        if not lhs_ctx.suffixOp():
            # verificar si es constante
            if isinstance(sym, VariableSymbol) and getattr(sym, "const", False):
                raise Exception(f"No se puede asignar a la constante '{base_text}'")
            
            addr_info = self._addr_for_identifier(base_text)
            
            if isinstance(addr_info, tuple) and addr_info[0] == "attribute":
                _, obj, prop = addr_info
                self.emit("setprop", obj, prop, t_value)
            else:
                self.emit("store", t_value, None, addr_info)
            
            self.tm.release_ref(t_value)
            return t_value
        
        # Procesar la base
        if base_text == "this":
            current = self.current_this
        elif isinstance(sym, VariableSymbol):
            addr_info = self._addr_for_identifier(base_text)
            current = self.tm.new_temp()
            
            if isinstance(addr_info, tuple) and addr_info[0] == "attribute":
                _, obj, prop = addr_info
                self.emit("getprop", obj, prop, current)
            else:
                self.emit("load", addr_info, None, current)
        else:
            current = self.visit(lhs_ctx.primaryAtom())
        
        # Procesar todos los sufijos excepto el último
        suffixes = lhs_ctx.suffixOp()
        for i, sop in enumerate(suffixes[:-1]):
            first = sop.getChild(0).getText()
            
            if first == "(":
                # llamada a función - evaluar normalmente
                args = []
                if hasattr(sop, "arguments") and sop.arguments():
                    for e in sop.arguments().expression():
                        t_arg = self.visit(e)
                        self.tm.add_ref(t_arg)
                        args.append(t_arg)
                
                for j, t_arg in enumerate(args):
                    self.emit("param", t_arg, None, None)
                    self.tm.release_ref(t_arg)
                
                t_res = self.tm.new_temp()
                self.emit("call", current, len(args), t_res)
                current = t_res
                
            elif first == "[":
                # indexación
                idx_t = self.visit(sop.expression())
                t_out = self.tm.new_temp()
                self.emit("getidx", current, idx_t, t_out)
                self.tm.release_ref(idx_t)
                current = t_out
                
            elif first == ".":
                # propiedad
                prop = sop.getChild(1).getText()
                t_prop = self.tm.new_temp()
                self.emit("getprop", current, prop, t_prop)
                current = t_prop
        
        # Procesar el último sufijo (donde se hace la asignación)
        last_sop = suffixes[-1]
        first = last_sop.getChild(0).getText()
        
        if first == "[":
            # arr[i] = value
            idx_t = self.visit(last_sop.expression())
            self.tm.add_ref(idx_t)
            self.emit("setidx", current, idx_t, t_value)
            self.tm.release_ref(idx_t)
            
        elif first == ".":
            # obj.prop = value
            prop = last_sop.getChild(1).getText()
            self.emit("setprop", current, prop, t_value)
        else:
            raise Exception(f"No se puede asignar a sufijo '{first}'")
        
        self.tm.release_ref(t_value)
        return t_value
    
    def visitPropertyAssignExpr(self, ctx):
        """Maneja: leftHandSide '.' Identifier '=' assignmentExpr"""
        # obtener el objeto (leftHandSide)
        t_obj = self.visit(ctx.lhs)
        self.tm.add_ref(t_obj)
        
        # obtener el nombre de la propiedad
        prop_name = ctx.Identifier().getText()
        
        # evaluar el valor a asignar
        t_value = self.visit(ctx.assignmentExpr())
        self.tm.add_ref(t_value)
        
        # emitir setprop
        self.emit("setprop", t_obj, prop_name, t_value)
        
        self.tm.release_ref(t_obj)
        self.tm.release_ref(t_value)
        
        return t_value
    
    def visitExprNoAssign(self, ctx):
        """Maneja: conditionalExpr (cuando no hay asignación)"""
        return self.visit(ctx.conditionalExpr())
    
    def visitTernaryExpr(self, ctx):
        """Maneja: logicalOrExpr ('?' expression ':' expression)?"""
        # evaluar condición
        t_cond = self.visit(ctx.logicalOrExpr())
        
        # si no hay operador ternario, solo retornar la condición
        if not ctx.expression():
            return t_cond
        
        # labels para el ternario
        label_true = self.tm.newLabel()
        label_false = self.tm.newLabel()
        label_end = self.tm.newLabel()
        
        t_result = self.tm.new_temp()
        
        # if (cond) goto true_label
        self.tm.add_ref(t_cond)
        self.emit("iftrue_goto", t_cond, None, label_true)
        self.tm.release_ref(t_cond)
        
        # false branch
        self.emit("label", label_false)
        t_false = self.visit(ctx.expression(1))
        self.tm.add_ref(t_false)
        self.emit("copy", t_false, None, t_result)
        self.tm.release_ref(t_false)
        self.emit("goto", None, None, label_end)
        
        # true branch
        self.emit("label", label_true)
        t_true = self.visit(ctx.expression(0))
        self.tm.add_ref(t_true)
        self.emit("copy", t_true, None, t_result)
        self.tm.release_ref(t_true)
        
        self.emit("label", label_end)
        return t_result

    # --------------- clases -----------------------------

    def visitClassDeclaration(self, ctx):
        # Nombre de la clase
        if isinstance(ctx.Identifier(), list):
            class_name = ctx.Identifier()[0].getText()
        else:
            class_name = ctx.Identifier().getText()

        prev_class = self.current_class
        self.current_class = class_name

        # Generamos el constructor de la clase
        constructor_label = f"_init_{class_name}"
        self.emit("label", constructor_label, None, None)

        # Parámetro implícito: this (recibido en FP[8])
        this_param = self.tm.new_temp()
        self.emit("load", "FP[8]", None, this_param)

        prev_this = self.current_this
        self.current_this = this_param

        # Inicializar atributos con valores por defecto o inicializadores
        for member in ctx.classMember():
            if hasattr(member, "variableDeclaration") and member.variableDeclaration():
                attr_ctx = member.variableDeclaration()
                attr_name = attr_ctx.Identifier().getText()

                # inicializador
                if attr_ctx.initializer():
                    t_init = self.visit(attr_ctx.initializer().expression())
                else:
                    # valor por defecto según tipo
                    t_init = self.tm.new_temp()

                    type_node = None
                    if hasattr(attr_ctx, "typeAnnotation") and attr_ctx.typeAnnotation():
                        type_ann = attr_ctx.typeAnnotation()
                        if hasattr(type_ann, "type_") and type_ann.type_():
                            type_node = type_ann.type_()
                        elif hasattr(type_ann, "type") and type_ann.type():
                            type_node = type_ann.type()
                    elif hasattr(attr_ctx, "type_") and attr_ctx.type_():
                        type_node = attr_ctx.type_()
                    elif hasattr(attr_ctx, "type") and attr_ctx.type():
                        type_node = attr_ctx.type()

                    type_text = type_node.getText() if type_node else None
                    if type_text == "string":
                        default_val = '""'
                    elif type_text == "boolean":
                        default_val = "false"
                    else:
                        default_val = "0"

                    self.emit("copy", default_val, None, t_init)

                # usar setprop para establecer el atributo
                self.emit("setprop", this_param, attr_name, t_init)

        # retornar this
        self.emit("ret", this_param, None, None)

        # Generar métodos de la clase
        for member in ctx.classMember():
            if hasattr(member, "functionDeclaration") and member.functionDeclaration():
                self.visit(member.functionDeclaration())

        self.current_this = prev_this
        self.current_class = prev_class
        return None

    # --------------- print ------------------------------

    def visitPrintStatement(self, ctx):
        t_expr = self.visit(ctx.expression())
        self.tm.add_ref(t_expr)
        self.emit("print", t_expr, None, None)
        self.tm.release_ref(t_expr)

    # --------------- left-hand-side (llamadas, index, props) ------------

    def visitLeftHandSide(self, ctx):
        base_text = ctx.primaryAtom().getText()
        sym = self._resolve_sym(base_text)

        # determinar base inicial
        if base_text == "this":
            acc_kind, acc_val = "value", self.current_this
        elif isinstance(sym, FunctionSymbol):
            acc_kind, acc_val = "func", (sym, sym.label or sym.name)
        elif isinstance(sym, VariableSymbol):
            # cargar el valor de la variable
            addr_info = self._addr_for_identifier(base_text)
            t0 = self.tm.new_temp()
            
            if isinstance(addr_info, tuple) and addr_info[0] == "attribute":
                _, obj, prop = addr_info
                self.emit("getprop", obj, prop, t0)
            else:
                self.emit("load", addr_info, None, t0)
            
            acc_kind, acc_val = "value", t0
        else:
            t0 = self.visit(ctx.primaryAtom())
            acc_kind, acc_val = "value", t0

        # sufijos: llamada, index, propiedad
        for sop in ctx.suffixOp():
            first = sop.getChild(0).getText()

            # --- llamada f(...) ---
            if first == "(":
                args = []
                if hasattr(sop, "arguments") and sop.arguments():
                    for e in sop.arguments().expression():
                        t_arg = self.visit(e)
                        self.tm.add_ref(t_arg)
                        args.append(t_arg)

                # Protocolo unificado de llamadas
                if acc_kind == "func":
                    func_sym, func_label = acc_val
                    
                    # Si es un método, pasar this como primer parámetro
                    if getattr(func_sym, "is_method", False):
                        self.emit("param", self.current_this, None, None)
                    
                    # pasar argumentos
                    for i, t_arg in enumerate(args):
                        self.emit("param", t_arg, None, None)
                        self.tm.release_ref(t_arg)
                    
                    # llamada
                    t_res = self.tm.new_temp()
                    self.emit("call", func_label, len(args), t_res)
                else:
                    # llamada indirecta (función como valor)
                    for i, t_arg in enumerate(args):
                        self.emit("param", t_arg, None, None)
                        self.tm.release_ref(t_arg)
                    
                    t_res = self.tm.new_temp()
                    self.emit("call", acc_val, len(args), t_res)

                acc_kind, acc_val = "value", t_res

            # --- indexación base[idx] ---
            elif first == "[":
                idx_t = self.visit(sop.expression())
                t_out = self.tm.new_temp()
                self.emit("getidx", acc_val, idx_t, t_out)
                self.tm.release_ref(idx_t)
                acc_kind, acc_val = "value", t_out

            # --- propiedad base.prop ---
            elif first == ".":
                prop = sop.getChild(1).getText()
                t_prop = self.tm.new_temp()
                self.emit("getprop", acc_val, prop, t_prop)
                acc_kind, acc_val = "value", t_prop

            else:
                raise Exception(f"Sufijo no reconocido: '{first}'")

        return acc_val

    # --------------- if / while / for / do-while / foreach --------------

    def visitIfStatement(self, ctx):
        cond_temp = self.visit(ctx.expression())
        label_true = self.tm.newLabel()
        label_false = self.tm.newLabel()
        label_end = self.tm.newLabel()

        self.tm.add_ref(cond_temp)
        self.emit("iffalse_goto", cond_temp, None, label_false)
        self.tm.release_ref(cond_temp)

        self.emit("label", label_true)
        self.visit(ctx.block(0))

        if len(ctx.block()) > 1:
            self.emit("goto", None, None, label_end)
            self.emit("label", label_false)
            self.visit(ctx.block(1))
            self.emit("label", label_end)
        else:
            self.emit("label", label_false)

    def visitWhileStatement(self, ctx):
        label_start = self.tm.newLabel()
        label_end = self.tm.newLabel()

        self.loop_stack.append((label_start, label_end, label_start))

        self.emit("label", label_start)
        cond_temp = self.visit(ctx.expression())
        self.tm.add_ref(cond_temp)
        self.emit("iffalse_goto", cond_temp, None, label_end)
        self.tm.release_ref(cond_temp)

        self.visit(ctx.block())
        self.emit("goto", None, None, label_start)
        self.emit("label", label_end)

        self.loop_stack.pop()

    def visitDoWhileStatement(self, ctx):
        label_start = self.tm.newLabel()
        label_end = self.tm.newLabel()

        self.loop_stack.append((label_start, label_end, label_start))

        self.emit("label", label_start)
        self.visit(ctx.block())

        cond_temp = self.visit(ctx.expression())
        self.tm.add_ref(cond_temp)
        self.emit("iftrue_goto", cond_temp, None, label_start)
        self.tm.release_ref(cond_temp)

        self.emit("label", label_end)
        self.loop_stack.pop()

    def visitForeachStatement(self, ctx):
        item_name = ctx.Identifier().getText()

        # evaluar colección
        t_collection = self.visit(ctx.expression())
        self.tm.add_ref(t_collection)

        label_start = self.tm.newLabel()
        label_end = self.tm.newLabel()
        label_update = self.tm.newLabel()

        self.loop_stack.append((label_start, label_end, label_update))

        # crear variable índice (temporal que se guarda en memoria)
        t_index = self.tm.new_temp()
        self.emit("copy", 0, None, t_index)  # index = 0

        # obtener longitud del array
        t_length = self.tm.new_temp()
        self.emit("array_length", t_collection, None, t_length)  # necesitarás agregar esto

        self.emit("label", label_start)

        # comprobar: index < length
        t_cond = self.tm.new_temp()
        self.emit("<", t_index, t_length, t_cond)
        self.emit("iffalse_goto", t_cond, None, label_end)

        # item = collection[index]
        t_item = self.tm.new_temp()
        self.emit("getidx", t_collection, t_index, t_item)

        # guardar en variable de iteración
        sym_item = self._resolve_sym(item_name)
        if isinstance(sym_item, VariableSymbol):
            addr = self._addr_for_symbol(sym_item, item_name)
        else:
            addr = item_name
        self.emit("store", t_item, None, addr)

        # cuerpo
        self.visit(ctx.block())

        # update: index++
        self.emit("label", label_update)
        t_one = self.tm.new_temp()
        self.emit("copy", 1, None, t_one)
        t_next_index = self.tm.new_temp()
        self.emit("+", t_index, t_one, t_next_index)
        self.emit("copy", t_next_index, None, t_index)

        self.emit("goto", None, None, label_start)
        self.emit("label", label_end)

        self.tm.release_ref(t_collection)
        self.loop_stack.pop()
    # --------------- break / continue -------------------

    def visitBreakStatement(self, ctx):
        if not self.loop_stack:
            raise Exception("break fuera de loop")
        _, label_end, _ = self.loop_stack[-1]
        self.emit("goto", None, None, label_end)

    def visitContinueStatement(self, ctx):
        if not self.loop_stack:
            raise Exception("continue fuera de loop")
        _, _, label_update = self.loop_stack[-1]
        self.emit("goto", None, None, label_update)

    # --------------- return -----------------------------

    def visitReturnStatement(self, ctx):
        value = self.visit(ctx.expression()) if ctx.expression() else None
        if value:
            self.emit("ret", value, None, None)
        else:
            self.emit("ret", None, None, None)

    # --------------- try/catch --------------------------

    def visitTryCatchStatement(self, ctx):
        try_label = self.tm.newLabel()
        catch_label = self.tm.newLabel()
        end_label = self.tm.newLabel()

        # registrar manejador de excepciones
        self.emit("push_handler", catch_label, None, None)
        
        # bloque try
        self.emit("label", try_label)
        self.visit(ctx.block(0))
        
        # si terminó sin excepción, saltar al final
        self.emit("pop_handler", None, None, None)
        self.emit("goto", None, None, end_label)

        # bloque catch
        self.emit("label", catch_label)
        exc_var = ctx.Identifier().getText()
        t_exc = self.tm.new_temp()
        self.emit("get_exception", None, None, t_exc)
        
        # guardar excepción en la variable
        sym = self._resolve_sym(exc_var)
        if isinstance(sym, VariableSymbol):
            addr = self._addr_for_symbol(sym, exc_var)
        else:
            addr = exc_var
        self.emit("store", t_exc, None, addr)
        
        self.visit(ctx.block(1))
        
        self.emit("label", end_label)

    # --------------- funciones --------------------------

    def visitFunctionDeclaration(self, ctx):
        func_name = ctx.Identifier().getText()

        # obtener símbolo
        sym = self._resolve_sym(func_name)

        # si es método de clase, prefijarlo con el nombre de la clase
        if sym and getattr(sym, "is_method", False):
            func_label = f"{sym.class_name}_{func_name}"
        else:
            func_label = func_name

        # crear label de función
        self.emit("label", func_label, None, None)

        # establecer frame actual de this (si es método)
        prev_this = self.current_this
        if sym and getattr(sym, "is_method", False):
            # cargar this del primer parámetro
            this_temp = self.tm.new_temp()
            self.emit("load", "FP[8]", None, this_temp)
            self.current_this = this_temp

        # visitar el cuerpo de la función
        self.visit(ctx.block())

        # agregar ret implícito si la función terminó sin return explícito
        self.emit("ret", None, None, None)

        self.current_this = prev_this