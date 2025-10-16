"""
Implementa la tabla de símbolos y los alcances para el analisis semántico del lenguaje 

El TypeSymbol: representa un tipo 

VarableSymbol: representa una variable con nombre, tipo, si es constante, inicializada y referencia al nodo de declaraci[on 

Scope:  el alcance con símbolos definidos y referencia el scope padre, este permite definir y resolver símbolos en la cadena de scopes 

SymbolTable: administra los scopes y los tipos, tiene el scope global el actual y los metodos para crear, entrar y salir de scopes, define y resulve variables y funciones y obtiene los tipos. 
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List

# tabla de simbolo por alcance
# estructura de datos que guarda informacion de los nombres de las variables que hay en un lenguaje de programacion

#representa un tipo, para listas una name="list" 
@dataclass
class TypeSymbol:
    name: str
    # Para listas tipadas como: list<elem>
    elem: Optional["TypeSymbol"] = None
    fields: Optional[Dict[str,'TypeSymbol']] = None  # para clases
    size: Optional[int] = None            # tamaño en bytes 
    align: int = 4                        # alineación por defecto

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeSymbol):
            return False
        return self.name == other.name and self.elem == other.elem

    def __repr__(self) -> str:
        if self.name == "list":
            return f"list<{self.elem!r}>" if self.elem else "list<?>"
        return self.name

# representa una variable en la tabla de simbolos
@dataclass
class VariableSymbol:
    name: str
    type: TypeSymbol
    const: bool = False
    initialized: bool = False
    decl_node: Any = None
    line: int = -1
    col: int = -1
    storage: str = "stack"   # "global"|"stack"|"param"|"field"
    offset: int = 0          # relativo a FP (stack/param) o a base de objeto (field)
    seg: Optional[str] = None  # por si se usa ".data/.bss"para globals

# representa una funcion en la tabla de simbolos
@dataclass
class FunctionSymbol:
    #  no defaults
    name: str
    return_type: TypeSymbol
    # defaults 
    params: List[VariableSymbol] = field(default_factory=list)
    is_defined: bool = False
    decl_node: Any = None
    line: int = -1
    col: int = -1
    label: Optional[str] = None
    frame_size: int = 0
    param_offsets: Dict[str,int] = None
    local_offsets: Dict[str,int] = None
    has_this: bool = False   # métodos

# representa un alcance en la tabla de simbolos
# crea un scope con padre opcional
class Scope:
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Any] = {}
        self.children: List['Scope'] = []   # <-- lista de hijos
        if parent:
            parent.children.append(self)   # <-- registrar hijo en el padre


    #define un simbolo nuevo en el scope actual
    def define(self, sym):
        if sym.name in self.symbols:
            raise Exception(f"Error: '{sym.name}' ya está definido en este alcance.")
        self.symbols[sym.name] = sym

    # busca un simbolo por cadena de scopez hasta la raiz
    def resolve(self, name: str) -> Optional[Any]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.resolve(name)
        return None

# representa la tabla de simbolos completa   
# # inicializa el scope global y registra los tipos base 
#administra scopes y tipos, expone utilidades para definir y resolver simbolos
class SymbolTable:
    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope

        # Tipos base conocidos
        self.types: Dict[str, TypeSymbol] = {
            "int":    TypeSymbol("int"),
            "float":  TypeSymbol("float"),
            "string": TypeSymbol("string"),
            "bool":   TypeSymbol("bool"),
            "void":   TypeSymbol("void"),
            "list":   TypeSymbol("list"),
        }

   # crea un nuevo scope, entra un nuevo scope hijo y lo devuelve
    def push_scope(self, name: str):
        self.current_scope = Scope(name, self.current_scope)
        return self.current_scope
    
    #sale al scope padre, error si ya esta en el global 
    def pop_scope(self):
        if self.current_scope.parent is None:
            raise Exception("Error: No se puede salir del alcance global.")
        self.current_scope = self.current_scope.parent

    # pop scope en otras palabras jaja
    def exit_scope(self):
        self.pop_scope()

    # resuelve un tipo
    def get_type(self, name: str) -> TypeSymbol:
        """
        Soporta:
          - tipos base: int, float, string, bool, void, nombres de clase
          - arreglos: T[], T[][]  -> list<T>, list<list<T>>
        """
        if name in self.types:
            return self.types[name]

        # soporte arreglos: int[], int[][]
        if name.endswith("]"):
            # contar dimensiones []
            dim = 0
            base = name
            while base.endswith("[]"):
                dim += 1
                base = base[:-2]
            # tipo base, puede ser primitivo o nombre de clase
            base_t = self.get_type(base)
            t = base_t
            for _ in range(dim):
                t = TypeSymbol("list", elem=t)
            return t

        # si es un nombre de clase ya registrado como tipo
        t = self.types.get(name)
        if t:
            return t

        raise Exception(f"Error: Tipo '{name}' no definido.")

    #define una variable en el scope actual
    def define_variable(self, var: VariableSymbol):
        self.current_scope.define(var)

    # define una funcion en el scope actual
    def define_function(self, func: FunctionSymbol):
        self.current_scope.define(func)

    # resuelve un simbolo desde el scope actual hacia arriba
    def resolve(self, name: str) -> Optional[Any]:
        return self.current_scope.resolve(name)
    



PRIM_SIZES = {"int":4, "float":8, "bool":1, "string":8, "void":0}

def sizeof(t: TypeSymbol) -> int:
    if t is None: return 0
    if t.name in PRIM_SIZES:
        return PRIM_SIZES[t.name]
    if t.name == "list":
        # modelo: cabecera fija (ptr + length) 2*8 = 16 bytes
        return 16
    if t.fields is not None:
        # clase/struct: suma de fields con alineación
        off = 0
        for fname, ftype in t.fields.items():
            sz = sizeof(ftype); al = max(1, ftype.align)
            off = ( (off + (al-1)) // al ) * al
            off += sz
        # alinea tamaño final
        return off
    # fallback
    return 8
