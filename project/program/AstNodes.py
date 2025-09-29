"""
Se definen todas las clases de nodos que forman el AST y se dan las dataclasses para la definición de las estructuras de datos.
Cada clase aquí representa un tipo de nodo en el AST, como declaraciones, sentencias, expresiones y los nodos tienen atributos que corresponden a los elementos sintácticos del lenguaje.

"""

from dataclasses import dataclass
from typing import List, Optional, Union, Any

@dataclass
class Program:
    statements: List[Any]

@dataclass
class VarDecl:
    name: str
    type: str
    is_const : bool = False
    init: Optional[Any] = None

@dataclass
class Param:
    name: str
    type: str

@dataclass
class FuncDecl:
    name: str
    params: List[Param]
    return_type: str
    body: List[Any]

@dataclass
class ClassDecl:
    name: str
    base: Optional[str] # class A : B { ... }  (puede ser None)
    methods: List['FuncDecl']
    properties: List['VarDecl']


# ------------------ sentencias --------------------
@dataclass
class Block:
    statements: List[Any]

@dataclass
class Assign: 
    target: Any
    expr: Any

@dataclass
class ExprStmt:
    expr: Any

@dataclass
class PrintStmt:
    expr: Any

@dataclass
class If: 
    condition: Any
    then_branch: Block
    else_branch: Optional[Block] = None

@dataclass
class While: 
    condition: Any
    body: Block

@dataclass
class DoWhile:
    body: Block
    condition: Any

@dataclass
class For: 
    body: Block
    init: Optional[Any] = None
    condition: Optional[Any] = None
    step : Optional[Any] = None

@dataclass
class Foreach:
    name: str
    iterable: Any
    body: Block

@dataclass
class TryCatch:
    try_block: Block
    var: str
    catch_block: Block

@dataclass
class Case:
    expr: Any
    statements: List[Any]

@dataclass
class Switch:
    expr: Any
    cases: List[Case]
    default: List[Any]


@dataclass
class Return: 
    expr: Optional[Any] = None


@dataclass
class Break: 
    pass

@dataclass
class Continue: 
    pass

# -------------------- expresiones ---------------------

@dataclass
class Var:
    name: str
    type: Optional[str] = None

@dataclass
class Call: 
    callee: Any    # puede ser Var/Member/etc.
    args: List[Any]

@dataclass
class Member: 
    object: Any
    name: str

@dataclass
class Index: 
    seq: Any
    index: Any

@dataclass
class UnOp: 
    op: str
    expr: Any

@dataclass
class BinOp: 
    left: Any
    op: str
    right: Any

@dataclass
class Ternary:
    condition: Any
    then_branch: Any
    else_branch: Any

@dataclass 
class New:
    class_name: str
    args: List[Any]


@dataclass
class This:
    pass

# -------- Literales ---------


@dataclass
class IntLiteral: 
    value: int

@dataclass
class StringLiteral: 
    value: str

@dataclass
class BooleanLiteral: 
    value: bool

@dataclass
class NullLiteral: 
    pass

@dataclass
class FloatLiteral: 
    value: float

@dataclass
class ListLiteral: 
    elements: List[Any]
