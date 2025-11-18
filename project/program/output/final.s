############################################
# Compiscript Runtime for MIPS (QTSPIM SAFE)
# - Heap estático (sin syscall 9)
# - Array new/get/set/len
# - Manejo de excepciones con stack propio
# - Stubs de objetos
# - cs_print para int / string
############################################

.data
#################################################
# Heap estático
#################################################
heap:           .space 200000        # 200 KB de heap
heap_ptr:       .word 0              # offset actual dentro de heap

#################################################
# Exception handler stack
#################################################
exc_stack:      .space 400           # 100 * 4 bytes
exc_sp:         .word 0              # índice actual (número de handlers)

# Código de la última excepción lanzada
last_exc_code:  .word 0

#################################################
# Mensajes de error
#################################################
err_bounds_msg: .asciiz "Runtime error: index out of bounds\n"
err_null_msg:   .asciiz "Runtime error: null reference\n"
err_nohandler:  .asciiz "Runtime error: unhandled exception\n"

.text
.globl cs_alloc_bytes
.globl cs_array_new
.globl cs_array_len
.globl cs_array_get
.globl cs_array_set
.globl cs_push_handler
.globl cs_pop_handler
.globl cs_throw
.globl cs_throw_bounds
.globl cs_throw_null
.globl cs_get_exception
.globl cs_alloc_object
.globl cs_getprop
.globl cs_setprop
.globl cs_print

############################################
# 1. Heap allocation (static heap, aligned)
############################################
# a0 = number of bytes
# v0 = pointer (ALIGNED to 4 bytes)
cs_alloc_bytes:
    # round up a0 to multiple of 4 → t2
    addu $t2, $a0, 3
    li   $t3, -4           # 0xFFFFFFFC
    and  $t2, $t2, $t3

    # load current heap_ptr
    la   $t0, heap_ptr
    lw   $t1, 0($t0)       # offset actual

    # v0 = heap + offset
    la   $v0, heap
    addu $v0, $v0, $t1

    # nuevo offset = offset + bytes_alineados
    addu $t1, $t1, $t2
    sw   $t1, 0($t0)

    jr   $ra

############################################
# 2. Arrays
############################################
# Layout:
#   arr:
#     [0] length   (word)
#     [1] data_ptr (word)

#################################################
# cs_array_new(a0 = length)
# returns:
#   v0 = new array pointer (header)
#################################################
cs_array_new:
    # guardar length original en t1
    move $t1, $a0

    # total_bytes = 8 + length * 4
    sll  $t0, $a0, 2        # length * 4
    addiu $t0, $t0, 8       # + header size

    # reservar en heap
    move $a0, $t0
    jal  cs_alloc_bytes     # v0 = base

    # inicializar header
    move $t2, $v0           # header ptr
    sw   $t1, 0($t2)        # [0] = length

    addiu $t3, $t2, 8       # data starts at +8
    sw   $t3, 4($t2)        # [1] = data ptr

    move $v0, $t2
    jr   $ra

#################################################
# cs_array_len(a0 = array)
# v0 = array length
#################################################
cs_array_len:
    beq  $a0, $zero, cs_throw_null
    lw   $v0, 0($a0)
    jr   $ra

#################################################
# cs_array_get(a0 = array, a1 = index)
# v0 = arr[index]
#################################################
cs_array_get:
    beq  $a0, $zero, cs_throw_null

    lw   $t0, 0($a0)         # length
    bltz $a1, cs_throw_bounds
    bge  $a1, $t0, cs_throw_bounds

    lw   $t1, 4($a0)         # data pointer
    sll  $t2, $a1, 2
    addu $t1, $t1, $t2       # aligned add
    lw   $v0, 0($t1)
    jr   $ra

#################################################
# cs_array_set(a0 = array, a1 = index, a2 = value)
#################################################
cs_array_set:
    beq  $a0, $zero, cs_throw_null

    lw   $t0, 0($a0)
    bltz $a1, cs_throw_bounds
    bge  $a1, $t0, cs_throw_bounds

    lw   $t1, 4($a0)
    sll  $t2, $a1, 2
    addu $t1, $t1, $t2
    sw   $a2, 0($t1)
    jr   $ra

############################################
# 3. Exception handling
############################################

#################################################
# cs_push_handler(a0 = handler_label_address)
#################################################
cs_push_handler:
    la   $t0, exc_sp
    lw   $t1, 0($t0)        # sp index

    la   $t2, exc_stack
    sll  $t3, $t1, 2        # offset = sp * 4
    addu $t2, $t2, $t3

    sw   $a0, 0($t2)        # push handler address

    addiu $t1, $t1, 1
    sw   $t1, 0($t0)
    jr   $ra

#################################################
# cs_pop_handler()
#################################################
cs_pop_handler:
    la   $t0, exc_sp
    lw   $t1, 0($t0)

    addiu $t1, $t1, -1
    bltz  $t1, cs_no_handler

    sw   $t1, 0($t0)
    jr   $ra

#################################################
# cs_throw(a0 = error_code)
#################################################
cs_throw:
    # guardar código de excepción
    la   $t5, last_exc_code
    sw   $a0, 0($t5)

    la   $t0, exc_sp
    lw   $t1, 0($t0)

    addiu $t1, $t1, -1      # pop
    bltz  $t1, cs_no_handler

    sw   $t1, 0($t0)

    la   $t2, exc_stack
    sll  $t3, $t1, 2
    addu $t2, $t2, $t3

    lw   $t4, 0($t2)        # handler address
    jr   $t4

#################################################
# Specific throw helpers
#################################################
cs_throw_bounds:
    li $a0, 1
    j  cs_throw

cs_throw_null:
    li $a0, 2
    j  cs_throw

#################################################
# Obtener código de excepción actual
# v0 = last_exc_code
#################################################
cs_get_exception:
    la  $t0, last_exc_code
    lw  $v0, 0($t0)
    jr  $ra

#################################################
# No handler disponible → imprimir mensaje y salir
#################################################
cs_no_handler:
    la   $t0, last_exc_code
    lw   $t1, 0($t0)

    li   $t2, 1
    beq  $t1, $t2, _exc_bounds
    li   $t2, 2
    beq  $t1, $t2, _exc_null

    # código desconocido
    la   $a0, err_nohandler
    j    _exc_print_exit

_exc_bounds:
    la   $a0, err_bounds_msg
    j    _exc_print_exit

_exc_null:
    la   $a0, err_null_msg

_exc_print_exit:
    li   $v0, 4
    syscall
    li   $v0, 10
    syscall

############################################
# 4. Object support (STUBS)
############################################

#################################################
# cs_alloc_object(type_id) → v0 = new object
# Por ahora: objeto de 8 bytes:
#   [0] vtable ptr (0)
#   [1] campo dummy (0)
#################################################
cs_alloc_object:
    li   $a0, 8          # bytes a reservar
    jal  cs_alloc_bytes

    sw   $zero, 0($v0)   # vtable ptr
    sw   $zero, 4($v0)   # un campo dummy
    jr   $ra

#################################################
# cs_setprop(object, prop_name, value)
# STUB: no hace nada por ahora
#################################################
cs_setprop:
    jr   $ra

#################################################
# cs_getprop(object, prop_name) → v0
# STUB: siempre regresa 0
#################################################
cs_getprop:
    move $v0, $zero
    jr   $ra

############################################
# cs_print(a0)
# Si es dirección válida dentro de .data → string
# Si no → número
############################################
cs_print:
    # strings: 0x1000_0000 - 0x1004_0000 (QtSPIM)
    li   $t1, 0x10000000
    blt  $a0, $t1, _print_int

    # es string
    li   $v0, 4
    syscall
    jr   $ra

_print_int:
    li   $v0, 1
    syscall
    jr   $ra


###########################################
# Jump automático a main (Compiscript)
###########################################

.globl main
j main

# ===== Compiscript Program =====

.data
LSTR1: .asciiz "name"
LSTR2: .asciiz "name"
LSTR3: .asciiz " makes a sound."
LSTR4: .asciiz "name"
LSTR5: .asciiz " barks."
LSTR6: .asciiz "Hello, Compiscript!"
LSTR7: .asciiz "5 + 1 = "
LSTR8: .asciiz "Greater than 5"
LSTR9: .asciiz "5 or less"
LSTR10: .asciiz "Result is now "
LSTR11: .asciiz "Loop index: "
LSTR12: .asciiz "Number: "
LSTR13: .asciiz "It's seven"
LSTR14: .asciiz "It's six"
LSTR15: .asciiz "Something else"
LSTR16: .asciiz "Risky access: "
LSTR17: .asciiz "Caught an error: "
LSTR18: .asciiz "Rex"
LSTR19: .asciiz "First number: "
LSTR20: .asciiz "Multiples of 2: "
LSTR21: .asciiz ", "
LSTR22: .asciiz "Program finished."

# include runtime (ya está cargado por separado)

.text
.globl main

makeAdder:
lw $t1, 64($fp)
li $t2, 1
move $t0, $t1
move $t1, $t2
addu $t3, $t0, $t1
move $v0, $t3
jr $ra
jr $ra
Animal.constructor:
lw $t3, 64($fp)
la $t2, this
move $a0, $t2
la $a1, LSTR1
move $a2, $t3
jal cs_setprop
jr $ra
Animal.speak:
la $t3, this
move $a0, $t3
la $a1, LSTR2
jal cs_getprop
move $t2, $v0
la $t3, LSTR3
move $t0, $t2
move $t1, $t3
addu $t1, $t0, $t1
move $v0, $t1
jr $ra
jr $ra
Dog.speak:
la $t1, this
move $a0, $t1
la $a1, LSTR4
jal cs_getprop
move $t3, $v0
la $t1, LSTR5
move $t0, $t3
move $t1, $t1
addu $t2, $t0, $t1
move $v0, $t2
jr $ra
jr $ra
getMultiples:
li $a0, 5
jal cs_array_new
move $t2, $v0
lw $t1, 64($fp)
li $t3, 1
move $t0, $t1
move $t1, $t3
mul $t4, $t0, $t1
move $a0, $t2
li $a1, 0
move $a2, $t4
jal cs_array_set
lw $t4, 64($fp)
li $t3, 2
move $t0, $t4
move $t1, $t3
mul $t1, $t0, $t1
move $a0, $t2
li $a1, 1
move $a2, $t1
jal cs_array_set
lw $t1, 64($fp)
li $t3, 3
move $t0, $t1
move $t1, $t3
mul $t4, $t0, $t1
move $a0, $t2
li $a1, 2
move $a2, $t4
jal cs_array_set
lw $t4, 64($fp)
li $t3, 4
move $t0, $t4
move $t1, $t3
mul $t1, $t0, $t1
move $a0, $t2
li $a1, 3
move $a2, $t1
jal cs_array_set
lw $t1, 64($fp)
li $t3, 5
move $t0, $t1
move $t1, $t3
mul $t4, $t0, $t1
move $a0, $t2
li $a1, 4
move $a2, $t4
jal cs_array_set
sw $t2, 0($fp)
lw $t2, 0($fp)
move $v0, $t2
jr $ra
jr $ra
factorial:
lw $t2, 64($fp)
li $t4, 1
move $t0, $t4
move $t1, $t2
slt $t3, $t0, $t1
xori $t3, $t3, 1
move $t0, $t3
beq $t0, $zero, L1
li $t3, 1
move $v0, $t3
jr $ra
L1:
lw $t3, 64($fp)
lw $t4, 64($fp)
li $t2, 1
move $t0, $t4
move $t1, $t2
subu $t1, $t0, $t1
move $t0, $t1
addi $sp, $sp, -4
sw $t0, 0($sp)
jal factorial
move $t1, $v0
addi $sp, $sp, 4
move $t0, $t3
move $t1, $t1
mul $t2, $t0, $t1
move $v0, $t2
jr $ra
jr $ra
main:
move $fp, $sp
li $t2, 314
sw $t2, 0($fp)
la $t2, LSTR6
sw $t2, 16($fp)
li $a0, 5
jal cs_array_new
move $t2, $v0
li $t1, 1
move $a0, $t2
li $a1, 0
move $a2, $t1
jal cs_array_set
li $t1, 2
move $a0, $t2
li $a1, 1
move $a2, $t1
jal cs_array_set
li $t1, 3
move $a0, $t2
li $a1, 2
move $a2, $t1
jal cs_array_set
li $t1, 4
move $a0, $t2
li $a1, 3
move $a2, $t1
jal cs_array_set
li $t1, 5
move $a0, $t2
li $a1, 4
move $a2, $t1
jal cs_array_set
sw $t2, 52($fp)
li $a0, 2
jal cs_array_new
move $t2, $v0
li $a0, 2
jal cs_array_new
move $t1, $v0
li $t3, 1
move $a0, $t1
li $a1, 0
move $a2, $t3
jal cs_array_set
li $t3, 2
move $a0, $t1
li $a1, 1
move $a2, $t3
jal cs_array_set
move $a0, $t2
li $a1, 0
move $a2, $t1
jal cs_array_set
li $a0, 2
jal cs_array_new
move $t1, $v0
li $t3, 3
move $a0, $t1
li $a1, 0
move $a2, $t3
jal cs_array_set
li $t3, 4
move $a0, $t1
li $a1, 1
move $a2, $t3
jal cs_array_set
move $a0, $t2
li $a1, 1
move $a2, $t1
jal cs_array_set
sw $t2, 116($fp)
li $t2, 5
move $t0, $t2
addi $sp, $sp, -4
sw $t0, 0($sp)
jal makeAdder
move $t2, $v0
addi $sp, $sp, 4
sw $t2, 180($fp)
la $t2, LSTR7
lw $t1, 180($fp)
move $t0, $t2
move $t1, $t1
addu $t3, $t0, $t1
move $a0, $t3
jal cs_print
lw $t3, 180($fp)
li $t1, 5
move $t0, $t1
move $t1, $t3
slt $t2, $t0, $t1
move $t0, $t2
beq $t0, $zero, L3
la $t2, LSTR8
move $a0, $t2
jal cs_print
j L4
L3:
la $t2, LSTR9
move $a0, $t2
jal cs_print
L4:
L5:
lw $t2, 180($fp)
li $t1, 10
move $t0, $t2
move $t1, $t1
slt $t3, $t0, $t1
move $t0, $t3
beq $t0, $zero, L6
lw $t3, 180($fp)
li $t1, 1
move $t0, $t3
move $t1, $t1
addu $t2, $t0, $t1
sw $t2, 180($fp)
j L5
L6:
L7:
la $t2, LSTR10
lw $t1, 180($fp)
move $t0, $t2
move $t1, $t1
addu $t3, $t0, $t1
move $a0, $t3
jal cs_print
lw $t3, 180($fp)
li $t1, 1
move $t0, $t3
move $t1, $t1
subu $t2, $t0, $t1
sw $t2, 180($fp)
lw $t2, 180($fp)
li $t1, 7
move $t0, $t1
move $t1, $t2
slt $t3, $t0, $t1
move $t0, $t3
bne $t0, $zero, L7
L8:
li $t3, 0
la $t9, i
sw $t3, 0($t9)
L9:
la $t3, i
li $t1, 3
move $t0, $t3
move $t1, $t1
slt $t2, $t0, $t1
move $t0, $t2
beq $t0, $zero, L10
la $t2, LSTR11
la $t1, i
move $t0, $t2
move $t1, $t1
addu $t3, $t0, $t1
move $a0, $t3
jal cs_print
L11:
la $t3, i
li $t1, 1
move $t0, $t3
move $t1, $t1
addu $t2, $t0, $t1
la $t9, i
sw $t2, 0($t9)
j L9
L10:
lw $t2, 52($fp)
li $t1, 0
move $a0, $t2
jal cs_array_len
move $t3, $v0
L12:
move $t0, $t1
move $t1, $t3
slt $t4, $t0, $t1
move $t0, $t4
beq $t0, $zero, L13
move $a0, $t2
move $a1, $t1
jal cs_array_get
move $t5, $v0
la $t9, n
sw $t5, 0($t9)
la $t6, n
li $t7, 3
move $t0, $t6
move $t1, $t7
xor $t8, $t0, $t1
sltiu $t8, $t8, 1
move $t0, $t8
beq $t0, $zero, L15
j L14
L15:
la $t8, LSTR12
la $t7, n
move $t0, $t8
move $t1, $t7
addu $t6, $t0, $t1
move $a0, $t6
jal cs_print
la $t6, n
li $t7, 4
move $t0, $t7
move $t1, $t6
slt $t8, $t0, $t1
move $t0, $t8
beq $t0, $zero, L17
j L13
L17:
L14:
li $t8, 1
move $t0, $t1
move $t1, $t8
addu $t7, $t0, $t1
move $t1, $t7
j L12
L13:
lw $t2, 180($fp)
li $t6, 7
move $t0, $t2
move $t1, $t6
xor $t9, $t0, $t1
sltiu $t9, $t9, 1
move $t0, $t9
bne $t0, $zero, L20
li $t0, 6
move $t0, $t2
move $t1, $t0
xor $t1, $t0, $t1
sltiu $t1, $t1, 1
move $t0, $t1
bne $t0, $zero, L21
j L22
L20:
la $t2, LSTR13
move $a0, $t2
jal cs_print
L21:
la $t2, LSTR14
move $a0, $t2
jal cs_print
L22:
la $t2, LSTR15
move $a0, $t2
jal cs_print
L19:
la $a0, L23
jal cs_push_handler
lw $t2, 52($fp)
li $t2, 10
move $a0, $t2
move $a1, $t2
jal cs_array_get
move $t3, $v0
la $t9, risky
sw $t3, 0($t9)
la $t3, LSTR16
la $t2, risky
move $t0, $t3
move $t1, $t2
addu $t2, $t0, $t1
move $a0, $t2
jal cs_print
jal cs_pop_handler
j L24
L23:
jal cs_get_exception
move $t2, $v0
la $t9, err
sw $t2, 0($t9)
la $t2, LSTR17
la $t3, err
move $t0, $t2
move $t1, $t3
addu $t4, $t0, $t1
move $a0, $t4
jal cs_print
L24:
la $t4, LSTR18
li $a0, 8
jal cs_alloc_object
move $t3, $v0
la $t0, _init_Dog
move $a0, $t3
jalr $t0
sw $t3, 196($fp)
lw $t3, 196($fp)
jal speak
move $t3, $v0
move $a0, $t3
jal cs_print
lw $t3, 52($fp)
li $t4, 0
move $a0, $t3
move $a1, $t4
jal cs_array_get
move $t2, $v0
sw $t2, 228($fp)
la $t2, LSTR19
lw $t4, 228($fp)
move $t0, $t2
move $t1, $t4
addu $t3, $t0, $t1
move $a0, $t3
jal cs_print
li $t3, 2
move $t0, $t3
addi $sp, $sp, -4
sw $t0, 0($sp)
jal getMultiples
move $t3, $v0
addi $sp, $sp, 4
sw $t3, 244($fp)
la $t3, LSTR20
lw $t4, 244($fp)
li $t2, 0
move $a0, $t4
move $a1, $t2
jal cs_array_get
move $t5, $v0
move $t0, $t3
move $t1, $t5
addu $t2, $t0, $t1
la $t5, LSTR21
move $t0, $t2
move $t1, $t5
addu $t3, $t0, $t1
lw $t5, 244($fp)
li $t2, 1
move $a0, $t5
move $a1, $t2
jal cs_array_get
move $t4, $v0
move $t0, $t3
move $t1, $t4
addu $t2, $t0, $t1
move $a0, $t2
jal cs_print
la $t2, LSTR22
move $a0, $t2
jal cs_print
li $v0, 0
jr $ra