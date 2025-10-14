from gen.CompiscriptVisitor import CompiscriptVisitor
from TempManager import TempManager
from IR import Instr

class IRGenerator(CompiscriptVisitor):
    def __init__(self):
        self.quads = []
        self.tm = TempManager()
        # Stack para manejar break/continue en loops anidados
        self.loop_stack = []  # [(label_start, label_end, label_update)]

    def emit(self, op, a=None, b=None, r=None):
        self.quads.append(Instr(op, a, b, r))

    def generate(self, tree):
        self.visit(tree)
        return self.quads

    def visitProgram(self, ctx):
        super().visitProgram(ctx) 
        return self.quads

    # expresiones literales
    def visitLiteralExpr(self, ctx):
        value = ctx.getText()
        t = self.tm.new_temp()
        self.emit('copy', value, None, t)
        return t
    
    # identificadores 
    def visitIdentifierExpr(self, ctx):
        name = ctx.getText()
        t = self.tm.new_temp()
        self.emit('load', name, None, t)
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
            t1 = t3  # resultado acumulado se vuelve el nuevo "izquierdo"

        return t1
    
    # expresiones multiplicativas (a * b, a / b, a % b)
    def visitMultiplicativeExpr(self, ctx):
        t1 = self.visit(ctx.unaryExpr(0))
        for i in range(1, len(ctx.unaryExpr())):
            t2 = self.visit(ctx.unaryExpr(i))
            op = ctx.getChild(2 * i - 1).getText()  # '*', '/', '%'

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
            self.emit('&&', t1, t2, t3)

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
            self.emit('||', t1, t2, t3)

            self.tm.release_ref(t1)
            self.tm.release_ref(t2)
            t1 = t3

        return t1
    
    # declaraciones
    def visitVariableDeclaration(self, ctx):
        # var name = expression;
        name = ctx.Identifier().getText()

        if ctx.initializer():  # tiene un valor inicial
            t_expr = self.visit(ctx.initializer().expression())
            self.tm.add_ref(t_expr)
            self.emit('store', t_expr, None, name)
            self.tm.release_ref(t_expr)
        else:
            self.emit('store', 'None', None, name)

        return None
    
    # asignacion x = expr
    def visitAssignment(self, ctx):
        name = ctx.Identifier().getText()
        t_expr = self.visit(ctx.expression(0))

        self.tm.add_ref(t_expr)
        self.emit('store', t_expr, None, name)
        self.tm.release_ref(t_expr)
        return None

    # prints
    def visitPrintStatement(self, ctx):
        t_expr = self.visit(ctx.expression())
        self.tm.add_ref(t_expr)
        self.emit('print', t_expr, None, None)
        self.tm.release_ref(t_expr)

    # llamadas a la funcion
    def visitCallExpr(self, ctx):
        # Obtener el nombre de la función (primer hijo antes del paréntesis)
        func_name = ctx.getChild(0).getText()

        # Evaluar los argumentos (si existen)
        args = []
        if ctx.arguments():
            for arg_ctx in ctx.arguments().expression():
                t_arg = self.visit(arg_ctx)
                args.append(t_arg)
                self.tm.add_ref(t_arg)

        # Enviar parámetros
        for i, t_arg in enumerate(args):
            self.emit('param', t_arg, None, f"p{i}")
            self.tm.release_ref(t_arg)

        # Recibir el retorno en un temporal
        t_result = self.tm.new_temp()
        self.emit('call', func_name, len(args), t_result)
        return t_result

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
        self.emit('iffalse_goto', cond_temp, None, label_false)
        self.tm.release_ref(cond_temp)

        # Bloque verdadero
        self.emit('label', label_true)
        self.visit(ctx.block(0))  # el primer bloque es el 'if'

        # Si existe 'else', procesarlo
        if len(ctx.block()) > 1:
            self.emit('goto', None, None, label_end)
            self.emit('label', label_false)
            self.visit(ctx.block(1))  # el segundo bloque es el 'else'
            self.emit('label', label_end)
        else:
            # Si no hay else, solo poner etiqueta falsa
            self.emit('label', label_false)

    # control de flujo - while
    def visitWhileStatement(self, ctx):
        """
        while (condition) {
            // body
        }
        """
        # Crear etiquetas
        label_start = self.tm.newLabel()
        label_end = self.tm.newLabel()
        
        # Agregar al stack de loops (sin label_update para while)
        self.loop_stack.append((label_start, label_end, label_start))
        
        # Etiqueta de inicio del loop
        self.emit('label', label_start)
        
        # Evaluar la condición
        cond_temp = self.visit(ctx.expression())
        self.tm.add_ref(cond_temp)
        
        # Si la condición es falsa, saltar al final
        self.emit('iffalse_goto', cond_temp, None, label_end)
        self.tm.release_ref(cond_temp)
        
        # Ejecutar el cuerpo del while
        self.visit(ctx.block())
        
        # Volver al inicio para re-evaluar la condición
        self.emit('goto', None, None, label_start)
        
        # Etiqueta de salida
        self.emit('label', label_end)
        
        # Remover del stack
        self.loop_stack.pop()

    # control de flujo - for
    def visitForStatement(self, ctx):
        """
        for (init; condition; update) {
            // body
        }
        """
        # 1. Inicialización
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
        self.emit('label', label_start)
        
        # 2. Condición (puede ser None)
        if ctx.expression(0):  # la primera expresión es la condición
            cond_temp = self.visit(ctx.expression(0))
            self.tm.add_ref(cond_temp)
            
            # Si la condición es falsa, saltar al final
            self.emit('iffalse_goto', cond_temp, None, label_end)
            self.tm.release_ref(cond_temp)
        
        # 3. Cuerpo del for
        self.visit(ctx.block())
        
        # 4. Update
        self.emit('label', label_update)
        if ctx.expression(1):  # la segunda expresión es el update
            update_temp = self.visit(ctx.expression(1))
            if update_temp:
                self.tm.add_ref(update_temp)
                self.tm.release_ref(update_temp)
        
        # Volver al inicio
        self.emit('goto', None, None, label_start)
        
        # Etiqueta de salida
        self.emit('label', label_end)
        
        # Remover del stack
        self.loop_stack.pop()

    # control de flujo - foreach
    def visitForeachStatement(self, ctx):
        """
        foreach (item in collection) {
            // body
        }
        
        Se traduce aproximadamente a:
        t_collection = evaluar collection
        t_index = 0
        t_length = length(t_collection)
        label_start:
            if t_index >= t_length goto label_end
            item = t_collection[t_index]
            // body
        label_update:
            t_index = t_index + 1
            goto label_start
        label_end:
        """
        item_name = ctx.Identifier().getText()
        
        # Evaluar la colección
        t_collection = self.visit(ctx.expression())
        self.tm.add_ref(t_collection)
        
        # Crear variable de índice
        t_index = self.tm.new_temp()
        self.emit('copy', '0', None, t_index)
        
        # Obtener longitud de la colección
        t_length = self.tm.new_temp()
        self.emit('length', t_collection, None, t_length)
        
        # Crear etiquetas
        label_start = self.tm.newLabel()
        label_end = self.tm.newLabel()
        label_update = self.tm.newLabel()
        
        # Agregar al stack de loops
        self.loop_stack.append((label_start, label_end, label_update))
        
        # Inicio del loop
        self.emit('label', label_start)
        
        # Condición: if (index >= length) goto end
        self.tm.add_ref(t_index)
        self.tm.add_ref(t_length)
        t_cond = self.tm.new_temp()
        self.emit('>=', t_index, t_length, t_cond)
        self.emit('if_goto', t_cond, None, label_end)
        self.tm.release_ref(t_index)
        self.tm.release_ref(t_length)
        
        # Obtener elemento actual: item = collection[index]
        self.tm.add_ref(t_collection)
        self.tm.add_ref(t_index)
        t_item = self.tm.new_temp()
        self.emit('getidx', t_collection, t_index, t_item)
        self.emit('store', t_item, None, item_name)
        self.tm.release_ref(t_collection)
        self.tm.release_ref(t_index)
        
        # Cuerpo del foreach
        self.visit(ctx.block())
        
        # Update: index = index + 1
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
        
        # Etiqueta de salida
        self.emit('label', label_end)
        
        # Limpiar referencias
        self.tm.release_ref(t_collection)
        
        # Remover del stack
        self.loop_stack.pop()

    # break statement
    def visitBreakStatement(self, ctx):
        """
        break; -> salta al final del loop más cercano
        """
        if not self.loop_stack:
            raise Exception("break statement outside of loop")
        
        _, label_end, _ = self.loop_stack[-1]
        self.emit('goto', None, None, label_end)
        return None

    # continue statement
    def visitContinueStatement(self, ctx):
        """
        continue; -> salta al update (for) o inicio (while) del loop más cercano
        """
        if not self.loop_stack:
            raise Exception("continue statement outside of loop")
        
        _, _, label_continue = self.loop_stack[-1]
        self.emit('goto', None, None, label_continue)
        return None