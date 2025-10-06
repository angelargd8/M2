
from gen.CompiscriptVisitor import CompiscriptVisitor
from TempManager import TempManager
from IR import Instr

class IRGenerator(CompiscriptVisitor):
    def __init__(self):
        self.quads = []
        self.tm = TempManager()

    def emit(self, op, a=None, b= None, r=None):
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
    
    # expresiones multiplicativas (a * b, a / b)
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

    # ver donde se reciclan
    def release_ref(self, t):
        if t:
            self.refcount[t] -= 1
            if self.refcount[t] <= 0:
                print(f"[release] {t} recycled.")
                self.pool.release(t)
                del self.refcount[t]

    #llamadas a la funcion
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

    #control de flujo
    def visitIfStatement(self, ctx):
        # Obtener la condición
        cond_temp = self.visit(ctx.expression())

        # Crear etiquetas
        label_true = self.tm.newLabel()
        label_false = self.tm.newLabel()
        label_end = self.tm.newLabel()

        # Generar salto condicional
        self.emit('if_true', cond_temp, None, label_true)
        self.emit('goto', None, None, label_false)

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

