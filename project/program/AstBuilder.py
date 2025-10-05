"""
Se define la clase AstBuilder que lo que hace es extender el visitor generado por ANTLR para transformar el parse tree en un AST.  
Las funciones de este archivo son: 
Mapear los nodos del parse tree a las clases dataclass que están en AstNode 
Implementar métodos Visit para cada tipo de nodo del lenguaje, como declaraciones 
Convierte los tipos textuales del lenguaje fuente a tipos internos como de integer a int 
Procesa declaraciones de variables, constantes, funciones, acceso a miembros, literales y estructuras de control 
"""

from gen.CompiscriptVisitor import CompiscriptVisitor
from gen.CompiscriptParser import CompiscriptParser
from AstNodes import *

#mapear tipos textuales a internos

def map_type(txt: str) -> str:
    t = txt.strip()
    t = t.replace("boolean", "bool").replace("integer", "int")
    return t

def type_from_annotation(typeAnn):
    if not typeAnn: 
        return None
    return map_type(typeAnn.type_().getText())

class AstBuilder(CompiscriptVisitor):
    # -------- Programa / bloques --------
    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        return Program([self.visit(s) for s in ctx.statement()])

    def visitBlock(self, ctx: CompiscriptParser.BlockContext):
        return Block([self.visit(s) for s in ctx.statement()])

    # -------- Declaraciones / sentencias --------
    def visitVariableDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        t = type_from_annotation(ctx.typeAnnotation())
        init = self.visit(ctx.initializer().expression()) if ctx.initializer() else None
        return VarDecl(name=name, type=t, is_const=False, init=init)

    def visitConstantDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        t = type_from_annotation(ctx.typeAnnotation())
        init = self.visit(ctx.expression())
        return VarDecl(name=name, type=t, is_const=True, init=init)

    def visitAssignment(self, ctx):
        #cuantas expresiones hay en el nodo
        exps = ctx.expression()

        # primer caso: x = expr; asignacion simple
        if ctx.Identifier() and len(exps) == 1:
            name = ctx.Identifier().getText()
            rhs = self.visit(exps[0])
            return Assign(target=Var(name), expr=rhs)

        #caso 2: asignacion a propiedad obj.prp = expr;
        if ctx.Identifier() and len(exps) == 2:
            obj = self.visit(exps[0])
            prop = ctx.Identifier().getText()
            rhs  = self.visit(exps[1])
            return Assign(target=Member(obj, prop), expr=rhs)

        #caso 3: otras formas de indexacion
        if len(exps) >= 2:
            lhs = self.visit(exps[0])
            idx = self.visit(exps[1])
            rhs = self.visit(exps[2]) if len(exps) >= 3 else None
            return Assign(target=Index(lhs, idx), expr=rhs)
            
        # Fallback por seguridad aunque no debería llegar aquí
        name = ctx.Identifier().getText() if ctx.Identifier() else "<anon>"
        rhs  = self.visit(exps[0]) if len(exps) else None
        return Assign(target=Var(name), expr=rhs)

    def visitExpressionStatement(self, ctx):
        return ExprStmt(self.visit(ctx.expression()))

    def visitPrintStatement(self, ctx):
        return PrintStmt(self.visit(ctx.expression()))

    def visitIfStatement(self, ctx):
        cond = self.visit(ctx.expression())
        thenb = self.visit(ctx.block(0))
        elsb  = self.visit(ctx.block(1)) if ctx.block(1) else None
        return If(cond, thenb, elsb)

    def visitWhileStatement(self, ctx):
        return While(self.visit(ctx.expression()), self.visit(ctx.block()))

    def visitDoWhileStatement(self, ctx):
        return DoWhile(self.visit(ctx.block()), self.visit(ctx.expression()))

    def visitForStatement(self, ctx):
        init = None
        if ctx.variableDeclaration():
            init = self.visit(ctx.variableDeclaration())
        elif ctx.assignment():
            init = self.visit(ctx.assignment())
        exprs = ctx.expression()
        cond = self.visit(exprs[0]) if len(exprs) >= 1 else None
        step = self.visit(exprs[1]) if len(exprs) >= 2 else None
        return For(body=self.visit(ctx.block()), init=init, condition=cond, step=step)

    def visitForeachStatement(self, ctx):
        return Foreach(ctx.Identifier().getText(), self.visit(ctx.expression()), self.visit(ctx.block()))

    def visitTryCatchStatement(self, ctx):
        return TryCatch(self.visit(ctx.block(0)), ctx.Identifier().getText(), self.visit(ctx.block(1)))

    def visitSwitchStatement(self, ctx):
        scrut = self.visit(ctx.expression())
        cases = []
        for c in ctx.switchCase():
            expr = self.visit(c.expression())
            stmts = [self.visit(s) for s in c.statement()]
            cases.append(Case(expr, stmts))
        default_stmts = [self.visit(s) for s in ctx.defaultCase().statement()] if ctx.defaultCase() else []
        return Switch(scrut, cases, default_stmts)

    def visitBreakStatement(self, ctx):    return Break()
    def visitContinueStatement(self, ctx): return Continue()
    def visitReturnStatement(self, ctx):  return Return(self.visit(ctx.expression()) if ctx.expression() else None)

    def visitFunctionDeclaration(self, ctx):
        name = ctx.Identifier().getText()
        params = []
        if ctx.parameters():
            for p in ctx.parameters().parameter():
                pname = p.Identifier().getText()
                ptype = map_type(p.type_().getText()) if p.type_() else None
                params.append(Param(pname, ptype))
        ret = map_type(ctx.type_().getText()) if ctx.type_() else "void"
        body = self.visit(ctx.block())
        return FuncDecl(name, params, ret, body)
    

    def visitClassDeclaration(self, ctx):
        cname = ctx.Identifier(0).getText()
        base  = ctx.Identifier(1).getText() if ctx.Identifier(1) else None
        methods, properties = [], []
        for m in ctx.classMember():
            node = self.visit(m)
            if isinstance(node, FuncDecl):   methods.append(node)
            elif isinstance(node, VarDecl):  properties.append(node)
        return ClassDecl(cname, base, methods, properties)
    

    def visitClassMember(self, ctx):
        if ctx.functionDeclaration():   return self.visit(ctx.functionDeclaration())
        if ctx.variableDeclaration():   return self.visit(ctx.variableDeclaration())
        if ctx.constantDeclaration():   return self.visit(ctx.constantDeclaration())
        return None

    # -------- Expresiones --------
    def visitExpression(self, ctx):        return self.visit(ctx.assignmentExpr())

    # assignmentExpr (labels)
    def visitAssignExpr(self, ctx):
        return Assign(self.visit(ctx.lhs), self.visit(ctx.assignmentExpr()))
    
    def visitPropertyAssignExpr(self, ctx):
        return Assign(Member(self.visit(ctx.lhs), ctx.Identifier().getText()),
                      self.visit(ctx.assignmentExpr()))
    
    def visitExprNoAssign(self, ctx):
        return self.visit(ctx.conditionalExpr())

    def visitTernaryExpr(self, ctx):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.logicalOrExpr())
        
        return Ternary(self.visit(ctx.logicalOrExpr()),
                       self.visit(ctx.expression(0)),
                       self.visit(ctx.expression(1)))

    def visitLogicalOrExpr(self, ctx):
        node = self.visit(ctx.logicalAndExpr(0))
        for i in range(1, len(ctx.logicalAndExpr())):
            node = BinOp(node, '||', self.visit(ctx.logicalAndExpr(i)))
        return node

    def visitLogicalAndExpr(self, ctx):
        node = self.visit(ctx.equalityExpr(0))
        for i in range(1, len(ctx.equalityExpr())):
            node = BinOp(node, '&&', self.visit(ctx.equalityExpr(i)))
        return node

    def visitEqualityExpr(self, ctx):        return self._chain_binops(ctx)
    def visitRelationalExpr(self, ctx):      return self._chain_binops(ctx)
    def visitAdditiveExpr(self, ctx):        return self._chain_binops(ctx)
    def visitMultiplicativeExpr(self, ctx):  return self._chain_binops(ctx)

    def _chain_binops(self, ctx):
        node = self.visit(ctx.getChild(0))
        i = 1
        while i < ctx.getChildCount():
            op  = ctx.getChild(i).getText()
            rhs = self.visit(ctx.getChild(i+1))
            node = BinOp(node, op, rhs)
            i += 2
        return node

    def visitUnaryExpr(self, ctx):
        if ctx.getChildCount() == 2:
            return UnOp(ctx.getChild(0).getText(), self.visit(ctx.getChild(1)))
        return self.visit(ctx.primaryExpr())

    def visitPrimaryExpr(self, ctx):
        if ctx.literalExpr():    return self.visit(ctx.literalExpr())
        if ctx.leftHandSide():   return self.visit(ctx.leftHandSide())
        return self.visit(ctx.expression())  # '(' expr ')'

    def visitLiteralExpr(self, ctx):
        if ctx.Literal():
            txt = ctx.Literal().getText()
            if txt.startswith('"'):
                return StringLiteral(txt[1:-1])  # quita comillas
            elif "." in txt:
                return FloatLiteral(float(txt))
            else:
                return IntLiteral(int(txt))
        
        if ctx.getText() == "null":
            return NullLiteral()
        if ctx.getText() == "true":
            return BooleanLiteral(True)
        if ctx.getText() == "false":
            return BooleanLiteral(False)
        if ctx.arrayLiteral():
            return self.visit(ctx.arrayLiteral())
        
        return None


    def visitArrayLiteral(self, ctx):
        return ListLiteral([self.visit(e) for e in ctx.expression()])

    # LHS = primaryAtom (suffixOp)*
    def visitLeftHandSide(self, ctx):
        node = self.visit(ctx.primaryAtom())
        for suf in ctx.suffixOp():

            if isinstance(suf, CompiscriptParser.CallExprContext):
                args = [self.visit(e) for e in suf.arguments().expression()] if suf.arguments() else []
                node = Call(node, args)

            elif isinstance(suf, CompiscriptParser.IndexExprContext):
                node = Index(node, self.visit(suf.expression()))

            elif isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                node = Member(node, suf.Identifier().getText())
        return node

    # primaryAtom (labels)
    def visitIdentifierExpr(self, ctx):
        return Var(ctx.Identifier().getText())
    
    def visitNewExpr(self, ctx):
        args = [self.visit(e) for e in ctx.arguments().expression()] if ctx.arguments() else []
        return New(ctx.Identifier().getText(), args)
    
    def visitThisExpr(self, ctx):
        return This()
