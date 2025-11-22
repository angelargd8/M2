# Layout en memoria (enteros de 4 bytes):
#
#   base:  [ length | elem0 | elem1 | elem2 | ... ]
#          0         4       8       12      ...
#
# IR esperado:
#   alloc_array  N,   -,   tArr
#   setidx       tArr,idx, tVal
#   getidx       tArr,idx, tDst
#   array_length tArr,-,   tLen
#
#       (0,1,2,...) o strings de dígitos ("0","1",...).
#       Esto basta para la inicialización de arreglos literales:
#       [1,2,3,4,5], [[1,2],[3,4]], etc.

class MIPSArrays:
    def __init__(self, codegen):
        self.cg = codegen  # referencia a MIPSCodeGen
        self.counter = 0   # para etiquetas únicas en setidx

    # ----------------- helpers internos -----------------

    def _get_array_reg(self, t_arr: str) -> str:
        """
        Obtiene el registro donde vive el puntero del array 't_arr'.
        """
        if t_arr not in self.cg.ptr_table:
            raise Exception(f"MIPSArrays: no hay registro para array '{t_arr}'")
        return self.cg.ptr_table[t_arr]

    def _is_int_like(self, v):
        return isinstance(v, int) or (isinstance(v, str) and v.isdigit())

    # ----------------- alloc_array -----------------

    def alloc_array(self, size, t_dest):
        """
        alloc_array size, -, t_dest

        Reserva (size + 1) * 4 bytes con syscall 9 (sbrk):
          - primer word: length
          - siguientes 'size' words: elementos
        Guarda el puntero en un registro asociado a t_dest.
        """
        if not self._is_int_like(size):
            raise Exception(f"alloc_array: tamaño no soportado '{size}'")

        size = int(size)
        total_bytes = (size + 1) * 4

        reg = self.cg.tm.get_reg(t_dest)

        self.cg.emit(f"    # alloc_array size={size}")
        self.cg.emit(f"    li $a0, {total_bytes}")
        self.cg.emit("    li $v0, 9")       # sbrk
        self.cg.emit("    syscall")
        self.cg.emit(f"    move {reg}, $v0")

        # guardar length en la primera celda
        self.cg.emit(f"    li $t9, {size}")
        self.cg.emit(f"    sw $t9, 0({reg})")

        # registrar que t_dest es un puntero a array
        self.cg.ptr_table[t_dest] = reg
        self.cg.temp_ptr[t_dest] = reg

    # ----------------- setidx -----------------

    def set_index(self, t_arr, index, t_val):
        """
        setidx t_arr, index, t_val

        t_arr : temporal con puntero al array
        index : entero (literal) o string de dígitos
        t_val : temporal entero o literal entero
        """
        self.counter += 1
        cid = self.counter

        reg_arr = self._get_array_reg(t_arr)

        def _pick_reg(exclude):
            # evitamos $t8 porque guarda el valor a escribir
            exclude = set(exclude) | {"$t8"}
            for r in ["$t9", "$t7", "$t6", "$t5", "$t4", "$t3", "$t2", "$t1"]:
                if r not in exclude:
                    return r
            return "$t0"

        # --- elegir registro para el valor (evitar colisión con reg_arr) ---
        value_reg = _pick_reg({reg_arr})

        # --- cargar valor a guardar ---
        if self._is_int_like(t_val):
            val = int(t_val)
            self.cg.emit(f"    li {value_reg}, {val}")
        elif isinstance(t_val, str) and t_val in self.cg.temp_int:
            val = int(self.cg.temp_int[t_val])
            self.cg.emit(f"    li {value_reg}, {val}")
        else:
            reg_val = self.cg.tm.get_reg(t_val)
            self.cg.emit(f"    move {value_reg}, {reg_val}")

        # --- índice estático ---
        if self._is_int_like(index) or (isinstance(index, str) and index in self.cg.temp_int):
            idx = int(index) if self._is_int_like(index) else int(self.cg.temp_int[index])
            offset = (idx + 1) * 4  # +1 por el length
            self.cg.emit(f"    # setidx {t_arr}[{idx}] = {t_val}")
            # bounds check simple: if idx >= length skip store
            len_reg = _pick_reg({reg_arr, value_reg})
            idx_reg = _pick_reg({reg_arr, value_reg, len_reg})
            self.cg.emit(f"    lw {len_reg}, 0({reg_arr})")
            self.cg.emit(f"    li {idx_reg}, {idx}")
            oob_lbl = f"setidx_oob_{t_arr}_{idx}_{cid}"
            done_lbl = f"setidx_done_{t_arr}_{idx}_{cid}"
            self.cg.emit(f"    bge {idx_reg}, {len_reg}, {oob_lbl}")
            self.cg.emit(f"    sw {value_reg}, {offset}({reg_arr})")
            self.cg.emit(f"    j {done_lbl}")
            self.cg.emit(f"{oob_lbl}:")
            self.cg.emit(f"    # índice fuera de rango, se ignora")
            self.cg.emit(f"{done_lbl}:")
            return

        # --- índice dinámico ---
        reg_idx = self.cg.tm.get_reg(index)
        len_reg = _pick_reg({reg_arr, reg_idx, value_reg})
        offset_reg = _pick_reg({reg_arr, reg_idx, len_reg, value_reg})
        self.cg.emit(f"    # setidx {t_arr}[{index}] = {t_val} (dinámico)")
        # bounds check: if idx >= length, skip store
        self.cg.emit(f"    lw {len_reg}, 0({reg_arr})")   # length
        oob_lbl = f"setidx_oob_dyn_{t_arr}_{cid}"
        done_lbl = f"setidx_done_dyn_{t_arr}_{cid}"
        self.cg.emit(f"    bge {reg_idx}, {len_reg}, {oob_lbl}")
        # offset = (idx + 1) * 4
        self.cg.emit(f"    sll {offset_reg}, {reg_idx}, 2")
        self.cg.emit(f"    addi {offset_reg}, {offset_reg}, 4")
        self.cg.emit(f"    add {offset_reg}, {reg_arr}, {offset_reg}")
        self.cg.emit(f"    sw {value_reg}, 0({offset_reg})")
        self.cg.emit(f"    j {done_lbl}")
        self.cg.emit(f"{oob_lbl}:")
        self.cg.emit(f"    # índice fuera de rango (dinámico), se ignora")
        self.cg.emit(f"{done_lbl}:")

    # ----------------- getidx -----------------

    def get_index(self, t_arr, index, t_dst):
        """
        getidx t_arr, index, t_dst

        t_arr : temporal con puntero al array
        index : entero (literal) o string de dígitos
        t_dst : temporal destino (guardamos el valor en un registro)
        """
        oob_static = f"getidx_oob_static_{t_dst}"
        oob_dyn = f"getidx_oob_dyn_{t_dst}"
        done_lbl = f"getidx_done_{t_dst}"
        reg_arr = self._get_array_reg(t_arr)
        reg_dst = self.cg.tm.get_reg(t_dst)

        # Índice conocido/literal
        if self._is_int_like(index):
            idx = int(index)
            offset = (idx + 1) * 4
            # bounds check: if idx >= length => reg_dst = 0
            self.cg.emit(f"    lw $t9, 0({reg_arr})")
            self.cg.emit(f"    li $t8, {idx}")
            self.cg.emit(f"    bge $t8, $t9, {oob_static}")
            self.cg.emit(f"    # getidx {t_arr}[{idx}] -> {t_dst}")
            self.cg.emit(f"    lw {reg_dst}, {offset}({reg_arr})")
            self.cg.emit(f"    j {done_lbl}")
        elif isinstance(index, str) and index in self.cg.temp_int:
            idx = int(self.cg.temp_int[index])
            offset = (idx + 1) * 4
            self.cg.emit(f"    lw $t9, 0({reg_arr})")
            self.cg.emit(f"    li $t8, {idx}")
            self.cg.emit(f"    bge $t8, $t9, {oob_static}")
            self.cg.emit(f"    # getidx {t_arr}[{idx}] -> {t_dst}")
            self.cg.emit(f"    lw {reg_dst}, {offset}({reg_arr})")
            self.cg.emit(f"    j {done_lbl}")
        else:
            # Índice dinámico: offset = (idx + 1) * 4
            reg_idx = self.cg.tm.get_reg(index)
            self.cg.emit(f"    # getidx {t_arr}[{index}] -> {t_dst} (dinámico)")
            self.cg.emit(f"    sll $t6, {reg_idx}, 2")   # idx * 4
            self.cg.emit("    addi $t6, $t6, 4")        # +4 para saltar length
            self.cg.emit(f"    lw $t8, 0({reg_arr})")    # length en t8
            self.cg.emit(f"    move $t7, {reg_idx}")
            self.cg.emit(f"    bge $t7, $t8, {oob_dyn}")
            self.cg.emit(f"    add $t6, {reg_arr}, $t6")
            self.cg.emit(f"    lw {reg_dst}, 0($t6)")
            self.cg.emit(f"    j {done_lbl}")

        # fallback para oob: setear 0
        # Para ramas estáticas y dinámicas usamos etiquetas únicas
        self.cg.emit(f"{oob_static}:")
        self.cg.emit(f"    li {reg_dst}, 0")
        self.cg.emit(f"    j {done_lbl}")
        self.cg.emit(f"{oob_dyn}:")
        self.cg.emit(f"    li {reg_dst}, 0")
        self.cg.emit(f"{done_lbl}:")

        # marcamos t_dst como "entero runtime" para que print_int_reg pueda usarlo
        self.cg.temp_int.pop(t_dst, None)  # valor dinámico, no constante
        # limpiar cualquier metadata previa de puntero/strings por si el temporal se reutiliza
        self.cg.ptr_table.pop(t_dst, None)
        self.cg.temp_ptr.pop(t_dst, None)
        self.cg.temp_string.pop(t_dst, None)

    # ----------------- array_length -----------------

    def length(self, t_arr, t_dst):
        """
        array_length t_arr, -, t_dst
        """
        reg_arr = self._get_array_reg(t_arr)
        reg_dst = self.cg.tm.get_reg(t_dst)

        self.cg.emit(f"    # array_length {t_arr} -> {t_dst}")
        self.cg.emit(f"    lw {reg_dst}, 0({reg_arr})")

        # marcar como entero (longitud)
        self.cg.temp_int.pop(t_dst, None)
