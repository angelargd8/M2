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
# NOTA: por ahora soportamos índices que sean literales enteros
#       (0,1,2,...) o strings de dígitos ("0","1",...).
#       Esto basta para la inicialización de arreglos literales:
#       [1,2,3,4,5], [[1,2],[3,4]], etc.

class MIPSArrays:
    def __init__(self, codegen):
        self.cg = codegen  # referencia a MIPSCodeGen

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
        if not self._is_int_like(index):
            raise Exception(f"setidx: índice dinámico aún no soportado ('{index}')")

        idx = int(index)
        offset = (idx + 1) * 4  # +1 por el length

        reg_arr = self._get_array_reg(t_arr)

        # cargar valor (literal o temporal) en $t8
        if self._is_int_like(t_val):
            val = int(t_val)
            self.cg.emit(f"    li $t8, {val}")
        elif isinstance(t_val, str) and t_val in self.cg.temp_int:
            # conocemos el valor constante
            val = int(self.cg.temp_int[t_val])
            self.cg.emit(f"    li $t8, {val}")
        else:
            # t_val es un temporal cuya info no tenemos como constante,
            # asumimos que ya vive en algún registro asignado por TempManager
            reg_val = self.cg.tm.get_reg(t_val)
            self.cg.emit(f"    move $t8, {reg_val}")

        self.cg.emit(f"    # setidx {t_arr}[{idx}] = {t_val}")
        self.cg.emit(f"    sw $t8, {offset}({reg_arr})")

    # ----------------- getidx -----------------

    def get_index(self, t_arr, index, t_dst):
        """
        getidx t_arr, index, t_dst

        t_arr : temporal con puntero al array
        index : entero (literal) o string de dígitos
        t_dst : temporal destino (guardamos el valor en un registro)
        """
        reg_arr = self._get_array_reg(t_arr)
        reg_dst = self.cg.tm.get_reg(t_dst)

        # Índice conocido/literal
        if self._is_int_like(index):
            idx = int(index)
            offset = (idx + 1) * 4
            self.cg.emit(f"    # getidx {t_arr}[{idx}] -> {t_dst}")
            self.cg.emit(f"    lw {reg_dst}, {offset}({reg_arr})")
        elif isinstance(index, str) and index in self.cg.temp_int:
            idx = int(self.cg.temp_int[index])
            offset = (idx + 1) * 4
            self.cg.emit(f"    # getidx {t_arr}[{idx}] -> {t_dst}")
            self.cg.emit(f"    lw {reg_dst}, {offset}({reg_arr})")
        else:
            # Índice dinámico: offset = (idx + 1) * 4
            reg_idx = self.cg.tm.get_reg(index)
            self.cg.emit(f"    # getidx {t_arr}[{index}] -> {t_dst} (dinámico)")
            self.cg.emit(f"    sll $t8, {reg_idx}, 2")   # idx * 4
            self.cg.emit("    addi $t8, $t8, 4")        # +4 para saltar length
            self.cg.emit(f"    add $t8, {reg_arr}, $t8")
            self.cg.emit(f"    lw {reg_dst}, 0($t8)")

        # marcamos t_dst como "entero runtime" para que print_int_reg pueda usarlo
        self.cg.temp_int[t_dst] = 0  # valor simbólico

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
        self.cg.temp_int[t_dst] = 0
