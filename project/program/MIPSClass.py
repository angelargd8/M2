# ================================================================
# Manejo de clases / objetos en MIPS
# - newobj Clase -> reserva memoria para los campos
# - setprop obj, nombre, valor -> sw en el offset del campo
# - getprop obj, nombre -> lw desde el offset del campo
#
# El SemanticAnalyzer deja en la tabla de tipos:
#   TypeSymbol.fields       : dict de nombre -> TypeSymbol
#   TypeSymbol._field_offsets: dict de nombre -> offset en bytes
#   TypeSymbol.size         : tamaño total en bytes
# Usamos esos datos para generar offsets seguros.
# ================================================================

class MIPSClass:
    def __init__(self, codegen):
        self.cg = codegen
        self.tm = codegen.tm
        self.obj_types = {}  # temp -> class_name
        self.global_obj_types = {}  # label -> class_name
        self.ptr_fields = {}  # class_name -> set(campos que son punteros)
        # reserva slot global para 'this'
        if "this: .word 0" not in self.cg.global_data:
            self.cg.global_data.append("this: .word 0")

    # ---------------------- helpers ----------------------
    def _get_type(self, class_name):
        if self.cg.symtab and class_name in self.cg.symtab.types:
            return self.cg.symtab.types[class_name]
        return None

    def _get_offset(self, class_name, prop):
        T = self._get_type(class_name)
        if T and getattr(T, "_field_offsets", None):
            return T._field_offsets.get(prop, 0)
        # fallback defensivo
        return 0

    def _get_field_type(self, class_name, prop):
        T = self._get_type(class_name)
        if T and T.fields and prop in T.fields:
            return T.fields[prop]
        return None

    def _is_ptr_type(self, t):
        if t is None:
            return False
        if t.name in ("string", "list", "array"):
            return True
        # tipos de clase u objetos tienen fields -> tratarlos como puntero
        if t.fields is not None:
            return True
        # cualquier tipo no primitivo conocido, considerarlo referencia
        return t.name not in ("int", "float", "bool", "void")

    def _ensure_ptr_reg(self, t_obj):
        """
        Devuelve un registro con el puntero al objeto.
        Respeta ptr_table si ya existe.
        """
        if t_obj in self.cg.ptr_table:
            return self.cg.ptr_table[t_obj]
        reg = self.tm.get_reg(t_obj)
        self.cg._load(t_obj, reg)
        self.cg.ptr_table[t_obj] = reg
        self.cg.temp_ptr[t_obj] = reg
        if t_obj not in self.obj_types and "this" in self.global_obj_types:
            self.obj_types[t_obj] = self.global_obj_types["this"]
        # Propagar tipo dinámico si viene de globals (incluido "this")
        if t_obj not in self.obj_types:
            if "this" in self.global_obj_types:
                self.obj_types[t_obj] = self.global_obj_types["this"]
            elif t_obj in self.global_obj_types:
                self.obj_types[t_obj] = self.global_obj_types[t_obj]
        return reg

    # ---------------------- ops ----------------------
    def new_object(self, class_name, t_dest):
        T = self._get_type(class_name)
        size = getattr(T, "size", 0) or 0
        if size <= 0:
            size = 4  # reserva mínima
        # redondear a palabra
        size = ((size + 3) // 4) * 4

        reg = self.tm.get_reg(t_dest)
        self.cg.emit(f"    # newobj {class_name} -> {t_dest}")
        self.cg.emit(f"    li $a0, {size}")
        self.cg.emit("    li $v0, 9")
        self.cg.emit("    syscall")
        self.cg.emit(f"    move {reg}, $v0")

        # registrar puntero
        self.cg.ptr_table[t_dest] = reg
        self.cg.temp_ptr[t_dest] = reg
        self.cg.temp_int.pop(t_dest, None)
        self.cg.temp_string.pop(t_dest, None)
        self.obj_types[t_dest] = class_name

    def set_prop(self, t_obj, prop, t_val):
        # necesitamos el offset de la clase; si no sabemos la clase, asumimos offset 0
        class_name = None
        # t_obj puede ser resultado de newobj -> temp_ptr ya set
        # Si conocemos el tipo del temporal por symtab global, tomarlo
        if isinstance(prop, str) and "." in prop:
            # por si viniera calificado, quedarnos con nombre de campo
            _, prop_name = prop.split(".", 1)
        else:
            prop_name = prop

        offset = 0
        cls = self.obj_types.get(t_obj)
        if cls:
            offset = self._get_offset(cls, prop_name)

        reg_obj = self._ensure_ptr_reg(t_obj)
        reg_val = self.tm.get_reg(t_val)
        self.cg._load(t_val, reg_val)

        # si el valor parece puntero (string/obj/array), recuerda el campo como puntero
        looks_ptr = (
            t_val in self.cg.temp_ptr
            or t_val in self.cg.ptr_table
            or t_val in self.cg.temp_string
            or (isinstance(t_val, str) and t_val.startswith('"'))
        )
        if class_name:
            pf = self.ptr_fields.setdefault(class_name, set())
            if looks_ptr:
                pf.add(prop_name)

        self.cg.emit(f"    # setprop {prop_name}")
        self.cg.emit(f"    sw {reg_val}, {offset}({reg_obj})")

    def get_prop(self, t_obj, prop, t_dst):
        if isinstance(prop, str) and "." in prop:
            _, prop_name = prop.split(".", 1)
        else:
            prop_name = prop

        offset = 0
        cls = self.obj_types.get(t_obj)
        if not cls:
            if t_obj in self.global_obj_types:
                cls = self.global_obj_types[t_obj]
            elif "this" in self.global_obj_types:
                cls = self.global_obj_types["this"]
        if cls:
            offset = self._get_offset(cls, prop_name)
        field_type = self._get_field_type(cls, prop_name) if cls else None
        reg_obj = self._ensure_ptr_reg(t_obj)
        if cls is None and t_obj in self.obj_types:
            cls = self.obj_types[t_obj]
        reg_dst = self.tm.get_reg(t_dst)
        # recomputar ptr_field con cls final
        ptr_field = cls in self.ptr_fields and prop_name in self.ptr_fields.get(cls, set())

        self.cg.emit(f"    # getprop {prop_name} -> {t_dst}")
        self.cg.emit(f"    lw {reg_dst}, {offset}({reg_obj})")

        # clasificar resultado según tipo del campo
        self.cg.temp_int.pop(t_dst, None)
        self.cg.temp_string.pop(t_dst, None)
        self.cg.ptr_table.pop(t_dst, None)
        self.cg.temp_ptr.pop(t_dst, None)

        if prop_name == "name" or self._is_ptr_type(field_type) or ptr_field:
            self.cg.ptr_table[t_dst] = reg_dst
            self.cg.temp_ptr[t_dst] = reg_dst
        # si no es ptr_type explícito, lo dejamos como valor numérico
