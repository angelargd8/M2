# =========================================s
# Compiscript Runtime para MIPS
# =========================================

.data
# --- Exception handler stack ---
exc_stack:    .space 400        # 100 handlers * 4 bytes
exc_sp:       .word 0           # top index

# --- Mensajes de error ---
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
.globl cs_alloc_object
.globl cs_getprop

############################################
# 1. Heap allocator
############################################
# a0 = bytes
# v0 = pointer
cs_alloc_bytes:
    li  $v0, 9         # sbrk
    syscall
    jr  $ra

############################################
# 2. Arrays
############################################
# Diseño:
#   arr:
#     [0] = length (word)
#     [4] = data_ptr (word)

# a0 = length
# v0 = pointer to array header
cs_array_new:
    # total = 8 + len*4
    sll $t0, $a0, 2        # len*4
    addi $t0, $t0, 8       # + header
    move $a1, $t0          # bytes
    jal cs_alloc_bytes     # v0 = base

    move $t1, $v0          # t1 = header
    sw   $a0, 0($t1)       # length
    addi $t2, $t1, 8       # data_ptr = base+8
    sw   $t2, 4($t1)
    jr   $ra

# a0 = array pointer
# v0 = length
cs_array_len:
    beq  $a0, $zero, cs_throw_null
    lw   $v0, 0($a0)
    jr   $ra

# a0 = array pointer
# a1 = index
# v0 = value (int)
cs_array_get:
    beq  $a0, $zero, cs_throw_null

    lw   $t0, 0($a0)        # len
    bltz $a1, cs_throw_bounds
    bge  $a1, $t0, cs_throw_bounds

    lw   $t1, 4($a0)        # data ptr
    sll  $t2, $a1, 2
    add  $t1, $t1, $t2
    lw   $v0, 0($t1)
    jr   $ra

# a0 = array pointer
# a1 = index
# a2 = value
cs_array_set:
    beq  $a0, $zero, cs_throw_null

    lw   $t0, 0($a0)        # len
    bltz $a1, cs_throw_bounds
    bge  $a1, $t0, cs_throw_bounds

    lw   $t1, 4($a0)        # data ptr
    sll  $t2, $a1, 2
    add  $t1, $t1, $t2
    sw   $a2, 0($t1)
    jr   $ra

############################################
# 3. Exception handling
############################################

# Stack layout:
#   exc_stack[0..99] : addresses (word)
#   exc_sp : number of handlers currently pushed

# a0 = handler address (label)
cs_push_handler:
    la   $t0, exc_sp
    lw   $t1, 0($t0)       # t1 = sp
    la   $t2, exc_stack
    sll  $t3, $t1, 2       # t3 = sp*4
    add  $t2, $t2, $t3
    sw   $a0, 0($t2)       # store handler
    addi $t1, $t1, 1
    sw   $t1, 0($t0)
    jr   $ra

cs_pop_handler:
    la   $t0, exc_sp
    lw   $t1, 0($t0)
    addi $t1, $t1, -1
    bltz $t1, cs_no_handler
    sw   $t1, 0($t0)
    jr   $ra

# a0 = error code (1=bounds,2=null,etc.)
cs_throw:
    la   $t0, exc_sp
    lw   $t1, 0($t0)       # sp
    addi $t1, $t1, -1
    bltz $t1, cs_no_handler
    sw   $t1, 0($t0)

    la   $t2, exc_stack
    sll  $t3, $t1, 2
    add  $t2, $t2, $t3
    lw   $t4, 0($t2)       # handler address
    jr   $t4

cs_throw_bounds:
    li   $a0, 1
    j    cs_throw

cs_throw_null:
    li   $a0, 2
    j    cs_throw

cs_no_handler:
    # print error_nohandler y terminar
    la   $a0, err_nohandler
    li   $v0, 4
    syscall
    li   $v0, 10
    syscall

############################################
# 4. Objetos (stubs)
############################################

# a0 = type_id (por ahora ignorado)
# v0 = pointer a objeto (dummy)
cs_alloc_object:
    # reservar sólo 8 bytes (vtable ptr + 1 campo)
    li   $a1, 8
    jal  cs_alloc_bytes
    # por ahora vtable=null y campo=0
    sw   $zero, 0($v0)
    sw   $zero, 4($v0)
    jr   $ra

# a0 = objeto
# a1 = prop_id
# v0 = valor
cs_getprop:
    # stub: solo retorna 0
    move $v0, $zero
    jr   $ra
