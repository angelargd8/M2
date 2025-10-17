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
        self.loop_stack = []  # (label_start, label_end, label_update)

    def emit(self, op, a=None, b=None, r=None):
        self.quads.append(Instr(op, a, b, r))

    def generate(self, tree):
        self.visit(tree)
        return self.quads

    # Programa principal
    def visitProgram(self, ctx):
        super().visitProgram(ctx)
        return self.quads

    # expresiones literales
    def visitLiteralExpr(self, ctx):
        value = ctx.getText()
        t = self.tm.new_temp()
        self.emit("copy", value, None, t)
        return t

    # identificadores 
    def visitIdentifierExpr(self, ctx):
        name = ctx.getText()
        symbol = self.symtab.resolve(name) if self.symtab else None

        if isinstance(symbol, VariableSymbol):
            if symbol.storage in ("stack", "param"):
                addr = f"FP[{symbol.offset}]"
            else:
                addr = symbol.name
        elif isinstance(symbol, FunctionSymbol):
            addr = symbol.label or symbol.name
        elif isinstance(symbol, TypeSymbol):
            addr = symbol.name
        else:
            addr = name

        t = self.tm.new_temp()
        self.emit("load", addr, None, t)
        print(f"[IRGEN] {name} → {addr}")
        return t

    # expresiones aditivas (a + b, a - b)
    def visitAdditiveExpr(self, ctx):
        # primera subexpresión
        t1 = self.visit(ctx.multiplicativeExpr(0))
        # si hay más operaciones, procesarlas en orden
        for i in range(1, len(ctx.multiplicativeExpr())):
            t2 = self.visit(ctx.multiplicativeExpr(i))
            op = ctx.getChild(2 * i - 1).getText()  # obtiene el '+' o '-'
            
            self.tm.add_ref(t1)
            self.tm.add_ref(t2)

            t3 = self.tm.new_temp()
            self.emit(op, t1, t2, t3)

            self.tm.release_ref(t1)
            self.tm.release_ref(t2)
            t1 = t3 # resultado acumulado se vuelve el nuevo "izquierdo"
        return t1

    # expresiones multiplicativas (a * b, a / b, a % b)
    def visitMultiplicativeExpr(self, ctx):
        t1 = self.visit(ctx.unaryExpr(0))
        for i in range(1, len(ctx.unaryExpr())):
            t2 = self.visit(ctx.unaryExpr(i))
            op = ctx.getChild(2 * i - 1).getText() # '*', '/', '%'
            
            self.tm.add_ref(t1)
            self.tm.add_ref(t2)
            
            t3 = self.tm.new_temp()
            self.emit(op, t1, t2, t3)
            
            self.tm.release_ref(t1)
            self.tm.release_ref(t2)
            t1 = t3
            
        return t1

    # expresiones relacionales (a < b, a <= b, a > b, a >= b)
    def visitRelationalExpr(self, ctx):
        t1 = self.visit(ctx.additiveExpr(0))

        for i in range(1, len(ctx.additiveExpr())):
            t2 = self.visit(ctx.additiveExpr(i))
            op = ctx.getChild(2 * i - 1).getText()  # '<', '<=', '>', '>='
            
            self.tm.add_ref(t1)
            self.tm.add_ref(t2)

            t3 = self.tm.new_temp()
            self.emit(op, t1, t2, t3)

            self.tm.release_ref(t1)
            self.tm.release_ref(t2)
            t1 = t3
        return t1

    # expresiones de igualdad (a == b, a != b)
    def visitEqualityExpr(self, ctx):
        t1 = self.visit(ctx.relationalExpr(0))
        for i in range(1, len(ctx.relationalExpr())):
            t2 = self.visit(ctx.relationalExpr(i))
            op = ctx.getChild(2 * i - 1).getText()  # '==', '!='

            self.tm.add_ref(t1)
            self.tm.add_ref(t2)

            t3 = self.tm.new_temp()
            self.emit(op, t1, t2, t3)

            self.tm.release_ref(t1)
            self.tm.release_ref(t2)
            t1 = t3

        return t1

    # expresiones lógicas AND (a && b)
    def visitLogicalAndExpr(self, ctx):
        t1 = self.visit(ctx.equalityExpr(0))

        for i in range(1, len(ctx.equalityExpr())):
            t2 = self.visit(ctx.equalityExpr(i))

            self.tm.add_ref(t1)
            self.tm.add_ref(t2)

            t3 = self.tm.new_temp()
            self.emit("&&", t1, t2, t3)

            self.tm.release_ref(t1)
            self.tm.release_ref(t2)
            t1 = t3

        return t1

    # expresiones lógicas OR (a || b)
    def visitLogicalOrExpr(self, ctx):
        t1 = self.visit(ctx.logicalAndExpr(0))

        for i in range(1, len(ctx.logicalAndExpr())):
            t2 = self.visit(ctx.logicalAndExpr(i))

            self.tm.add_ref(t1)
            self.tm.add_ref(t2)

            t3 = self.tm.new_temp()
            self.emit("||", t1, t2, t3)

            self.tm.release_ref(t1)
            self.tm.release_ref(t2)
            t1 = t3

        return t1

    # declaraciones y asignaciones
    def visitVariableDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        symbol = self.symtab.resolve(name) if self.symtab else None
        if isinstance(symbol, VariableSymbol):
            if symbol.storage in ("stack", "param"):
                addr = f"FP[{symbol.offset}]"
            else:
                addr = symbol.name
        else:
            addr = name
        if ctx.initializer():
            t_expr = self.visit(ctx.initializer().expression())
            self.tm.add_ref(t_expr)
            self.emit("store", t_expr, None, f"{name}({addr})")
            self.tm.release_ref(t_expr)
        else:
            pass
            # no se declara un none porque no tiene sentido 
            # self.emit("store", "None", None, addr)
        return None

    def visitConstantDeclaration(self, ctx):
    # Obtener nombre del identificador
        name = ctx.Identifier().getText()
        
        # Obtener símbolo asociado
        symbol = self.symtab.resolve(name) if self.symtab else None
        if isinstance(symbol, VariableSymbol):
            if symbol.storage in ("stack", "param"):
                addr = f"FP[{symbol.offset}]"
            else:
                addr = symbol.name
        else:
            addr = name

        # Evaluar la expresión de inicialización
        t_expr = self.visit(ctx.expression())
        self.tm.add_ref(t_expr)

        # Emitir el TAC para copiar el valor y almacenarlo
        self.emit("store", t_expr, None, f"{name}")

        # Liberar el temporal
        self.tm.release_ref(t_expr)

        # Marcar el símbolo como constante (si aplica)
        if symbol:
            symbol.const = True

        return None



    # asignacion x = expr
    def visitAssignment(self, ctx):
        name = ctx.Identifier().getText()
        t_expr = self.visit(ctx.expression(0))

        symbol = self.symtab.resolve(name) if self.symtab else None

        if isinstance(symbol, VariableSymbol):
            if symbol.storage in ("stack", "param"):
                addr = f"FP[{symbol.offset}]"
            else:
                addr = symbol.name
        else:
            addr = name

        self.tm.add_ref(t_expr)
        self.emit("store", t_expr, None, addr)
        self.tm.release_ref(t_expr)
        return None

    def visitPrintStatement(self, ctx):
        t_expr = self.visit(ctx.expression())
        self.tm.add_ref(t_expr)
        self.emit("print", t_expr, None, None)
        self.tm.release_ref(t_expr)

    # manejo de llamadas (leftHandSide) !!
    def visitLeftHandSide(self, ctx):
        #Permite llamadas, indexación y acceso a propiedades.

        base_text = ctx.primaryAtom().getText()
        sym = self.symtab.resolve(base_text) if self.symtab else None

        if isinstance(sym, FunctionSymbol):
            acc_kind, acc_val = "func", (sym.label or sym.name)

        elif isinstance(sym, VariableSymbol):
            if sym.storage in ("stack", "param"):
                addr = f"FP[{sym.offset}]"
            else:
                addr = sym.name
            t0 = self.tm.new_temp()
            self.emit("load", addr, None, t0)
            acc_kind, acc_val = "value", t0
        else:
            t0 = self.visit(ctx.primaryAtom())
            acc_kind, acc_val = "value", t0

        for sop in ctx.suffixOp():
            first = sop.getChild(0).getText()

            # Llamada
            if first == "(":
                args = []
                if hasattr(sop, "arguments") and sop.arguments():
                    for e in sop.arguments().expression():
                        t_arg = self.visit(e)
                        self.tm.add_ref(t_arg)
                        args.append(t_arg)

                func_sym = self.symtab.resolve(acc_val) if acc_kind == "func" else None

                # Paso de parametros
                if isinstance(func_sym, FunctionSymbol) and func_sym.param_offsets:
                    for i, (t_arg, p_sym) in enumerate(zip(args, func_sym.params)):
                        off = func_sym.param_offsets.get(p_sym.name, 8 * (i + 1))
                        self.emit("store", t_arg, None, f"FP[{off}]")
                        self.tm.release_ref(t_arg)
                else:
                    for i, t_arg in enumerate(args):
                        self.emit("param", t_arg, None, f"p{i}")
                        self.tm.release_ref(t_arg)

                # protocolo de llamada
                if isinstance(func_sym, FunctionSymbol):
                    self.emit("push", "FP", None, None)
                    self.emit("enter", func_sym.frame_size or 0, None, None)
                    self.emit("call", func_sym.label or func_sym.name, None, None)
                    t_res = self.tm.new_temp()
                    self.emit("move_ret", None, None, t_res)
                    self.emit("leave", None, None, None)
                    self.emit("pop", "FP", None, None)
                else:
                    t_res = self.tm.new_temp()
                    self.emit("call", acc_val, len(args), t_res)

                acc_kind, acc_val = "value", t_res

            # Indexacion 
            elif first == "[":
                idx_t = self.visit(sop.expression())
                t_out = self.tm.new_temp()
                self.emit("getidx", acc_val, idx_t, t_out)
                acc_kind, acc_val = "value", t_out

            # Propiedad 
            elif first == ".":
                prop = sop.getChild(1).getText()
                t_out = self.tm.new_temp()
                self.emit("getprop", acc_val, prop, t_out)
                acc_kind, acc_val = "value", t_out

            else:
                raise Exception(f"Sufijo no reconocido: '{first}'")

        return acc_val

    # control de flujo - if
    def visitIfStatement(self, ctx):
        # Obtener la condición
        cond_temp = self.visit(ctx.expression())
        # Crear etiquetas
        label_true = self.tm.newLabel()
        label_false = self.tm.newLabel()
        label_end = self.tm.newLabel()

        # Generar salto condicional
        self.tm.add_ref(cond_temp)
        self.emit("iffalse_goto", cond_temp, None, label_false)
        self.tm.release_ref(cond_temp)

        # Bloque verdadero
        self.emit("label", label_true)
        self.visit(ctx.block(0))  # el primer bloque es el 'if'

        # Si existe 'else', procesarlo
        if len(ctx.block()) > 1:
            self.emit("goto", None, None, label_end)
            self.emit("label", label_false)
            self.visit(ctx.block(1)) # el segundo bloque es el 'else'
            self.emit("label", label_end)
        else:
            # Si no hay else, solo poner etiqueta falsa
            self.emit("label", label_false)

    # control de flujo - while
    def visitWhileStatement(self, ctx):

        # Crear etiquetas
        label_start = self.tm.newLabel()
        label_end = self.tm.newLabel()

        # Agregar al stack de loops (sin label_update para while)
        self.loop_stack.append((label_start, label_end, label_start))
        
        # Etiqueta de inicio del loop
        self.emit("label", label_start)

        # Evaluar la condición
        cond_temp = self.visit(ctx.expression())
        self.tm.add_ref(cond_temp)

        # Si la condición es falsa, saltar al final
        self.emit("iffalse_goto", cond_temp, None, label_end)
        self.tm.release_ref(cond_temp)

        # Ejecutar el cuerpo del while
        self.visit(ctx.block())

        # Volver al inicio para re-evaluar la condición
        self.emit("goto", None, None, label_start)

        # Etiqueta de salida
        self.emit("label", label_end)

        # Remover del stack
        self.loop_stack.pop()

    # control de flujo - for
    def visitForStatement(self, ctx):

        # Inicialización
        if ctx.variableDeclaration():
            self.visit(ctx.variableDeclaration())
        elif ctx.assignment():
            self.visit(ctx.assignment())

        # Crear etiquetas
        label_start = self.tm.newLabel()
        label_end = self.tm.newLabel()
        label_update = self.tm.newLabel()

        # Agregar al stack de loops
        self.loop_stack.append((label_start, label_end, label_update))
        
        # Etiqueta de inicio del loop
        self.emit("label", label_start)

        # Condición (puede ser None)
        if ctx.expression(0):
            cond_temp = self.visit(ctx.expression(0))  # la primera expresión es la condición
            self.tm.add_ref(cond_temp)

            # Si la condición es falsa, saltar al final
            self.emit("iffalse_goto", cond_temp, None, label_end)
            self.tm.release_ref(cond_temp)

        # cuerpo del for
        self.visit(ctx.block())
        #update
        self.emit("label", label_update)
        if ctx.expression(1):
            update_temp = self.visit(ctx.expression(1))
            if update_temp:
                self.tm.add_ref(update_temp)
                self.tm.release_ref(update_temp)
        #volver al inicio
        self.emit("goto", None, None, label_start)
        #etiqueta de salida
        self.emit("label", label_end)
        #quitar del stack
        self.loop_stack.pop()

    # break statement
    def visitBreakStatement(self, ctx):
        if not self.loop_stack:
            raise Exception("break fuera de loop")
        _, label_end, _ = self.loop_stack[-1]
        self.emit("goto", None, None, label_end)

    # continue statement
    def visitContinueStatement(self, ctx):
        if not self.loop_stack:
            raise Exception("continue fuera de loop")
        _, _, label_update = self.loop_stack[-1]
        self.emit("goto", None, None, label_update)

    def visitForeachStatement(self, ctx):
        # foreach (Identifier in expression) block
        item_name = ctx.Identifier().getText()

        #Evaluar la colección
        t_collection = self.visit(ctx.expression())
        self.tm.add_ref(t_collection)

        # index = 0
        t_index = self.tm.new_temp()
        self.emit('copy', '0', None, t_index)

        #length = len(collection)
        t_length = self.tm.new_temp()
        self.emit('length', t_collection, None, t_length)

        #Etiquetas de control
        label_start = self.tm.newLabel()
        label_end = self.tm.newLabel()
        label_update = self.tm.newLabel()

        # Registrar en la pila de loops (para break/continue)
        self.loop_stack.append((label_start, label_end, label_update))

        #Inicio del loop
        self.emit('label', label_start)

        # Condición: if (index >= length) goto end
        self.tm.add_ref(t_index); self.tm.add_ref(t_length)
        t_cond = self.tm.new_temp()
        self.emit('>=', t_index, t_length, t_cond)
        self.emit('if_goto', t_cond, None, label_end)
        self.tm.release_ref(t_index); self.tm.release_ref(t_length)

        # item = collection[index]
        self.tm.add_ref(t_collection); self.tm.add_ref(t_index)
        t_item = self.tm.new_temp()
        self.emit('getidx', t_collection, t_index, t_item)
        self.tm.release_ref(t_collection); self.tm.release_ref(t_index)

        # store item en el destino (offsets si existe en la tabla)
        sym_item = self.symtab.resolve(item_name) if self.symtab else None
        if isinstance(sym_item, VariableSymbol):
            if sym_item.storage in ('stack', 'param'):
                addr = f"FP[{sym_item.offset}]"
            else:
                addr = sym_item.name
        else:
            # si no está en la tabla
            addr = item_name
        self.emit('store', t_item, None, addr)

        # Cuerpo del foreach
        self.visit(ctx.block())

        # label_update: index += 1
        self.emit('label', label_update)
        self.tm.add_ref(t_index)
        t_one = self.tm.new_temp()
        
        self.emit('copy', '1', None, t_one)
        t_new_index = self.tm.new_temp()
        
        self.emit('+', t_index, t_one, t_new_index)
        self.emit('copy', t_new_index, None, t_index)
        self.tm.release_ref(t_index)

        # Volver al inicio
        self.emit('goto', None, None, label_start)

        # Salida
        self.emit('label', label_end)

        # Limpiar refs y sacar del stack
        self.tm.release_ref(t_collection)
        self.loop_stack.pop()

    # return statement
    def visitReturnStatement(self, ctx):
        value = self.visit(ctx.expression()) if ctx.expression() else None
        if value:
            self.emit("ret", value, None, None)
        else:
            self.emit("ret", None, None, None)

    # try/catch
    def visitTryCatchStatement(self, ctx):
        try_label = self.tm.newLabel()
        end_label = self.tm.newLabel()
        catch_label = self.tm.newLabel()

        self.emit("try_begin", None, None, try_label)
        self.visit(ctx.block(0))  # bloque try
        self.emit("try_end", None, None, end_label)

        self.emit("catch_begin", ctx.Identifier().getText(), None, catch_label)
        self.visit(ctx.block(1))  # bloque catch
        self.emit("catch_end", None, None, end_label)
        