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