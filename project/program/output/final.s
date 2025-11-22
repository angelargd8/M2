

# ===== Compiscript Program =====

.data
this: .word 0
g_arr: .word 10, 20, 30, 40, 50
g_p1: .word 0
g_total: .word 0
exc_handler: .word 0
exc_value: .word 0
str_div_zero: .asciiz "division by zero"
nl: .asciiz "\n"
str_lbr: .asciiz "["
str_rbr: .asciiz "]"
str_comma: .asciiz ", "
str_array: .asciiz "[array]"
exc_tmp: .word 0

.text
.globl main
.globl cs_int_to_string
    la $ra, __program_exit
    jal main
__program_exit:
    li $v0, 10
    syscall

# ===== RUNTIME SUPPORT: cs_int_to_string =====
cs_int_to_string:
    addi $sp, $sp, -44
    sw $ra, 40($sp)
    sw $s0, 36($sp)
    sw $s1, 32($sp)
    sw $t0, 28($sp)
    sw $t1, 24($sp)
    sw $t2, 20($sp)
    sw $t3, 16($sp)
    sw $t4, 12($sp)
    sw $t5, 8($sp)
    sw $t6, 4($sp)
    sw $t7, 0($sp)
    move $s1, $a0
    li $a0, 12
    li $v0, 9
    syscall
    move $s0, $v0        # base buffer
    addi $t0, $s0, 11
    sb $zero, 11($s0)
    move $t2, $s1
    bne $t2, $zero, cs_its_nonzero
    li $t3, '0'
    sb $t3, 10($s0)
    addi $v0, $s0, 10
    j cs_its_done
cs_its_nonzero:
    li $t4, 0
    bltz $t2, cs_its_neg
    j cs_its_abs_ok
cs_its_neg:
    li $t4, 1
    subu $t2, $zero, $t2
cs_its_abs_ok:
    move $t1, $t0
cs_its_digit_loop:
    beq $t2, $zero, cs_its_digits_done
    li $t5, 10
    div $t2, $t5
    mfhi $t6
    mflo $t2
    addi $t6, $t6, 48
    sb $t6, -1($t1)
    addi $t1, $t1, -1
    j cs_its_digit_loop
cs_its_digits_done:
    beq $t4, $zero, cs_its_no_minus
    li $t7, '-'
    sb $t7, -1($t1)
    addi $t1, $t1, -1
cs_its_no_minus:
    move $v0, $t1
cs_its_done:
    lw $t7, 0($sp)
    lw $t6, 4($sp)
    lw $t5, 8($sp)
    lw $t4, 12($sp)
    lw $t3, 16($sp)
    lw $t2, 20($sp)
    lw $t1, 24($sp)
    lw $t0, 28($sp)
    lw $s1, 32($sp)
    lw $s0, 36($sp)
    lw $ra, 40($sp)
    addi $sp, $sp, 44
    jr $ra

Point.init:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    addi $sp, $sp, -32
    sw $s0, 0($sp)
    sw $s1, 4($sp)
    sw $s2, 8($sp)
    sw $s3, 12($sp)
    sw $s4, 16($sp)
    sw $s5, 20($sp)
    sw $s6, 24($sp)
    sw $s7, 28($sp)
    lw $t0, 8($fp)
    la $t1, this
    lw $t1, 0($t1)
    move $t0, $t0
    # setprop x
    sw $t0, 0($t1)
    lw $t0, 12($fp)
    la $t1, this
    lw $t1, 0($t1)
    move $t0, $t0
    # setprop y
    sw $t0, 4($t1)
Point.init_epilog:
    # ---- EPILOG ----
    lw $s0, 0($sp)
    lw $s1, 4($sp)
    lw $s2, 8($sp)
    lw $s3, 12($sp)
    lw $s4, 16($sp)
    lw $s5, 20($sp)
    lw $s6, 24($sp)
    lw $s7, 28($sp)
    addi $sp, $sp, 32
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    beq $ra, $zero, __program_exit
    jr $ra
Point.sum:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    addi $sp, $sp, -32
    sw $s0, 0($sp)
    sw $s1, 4($sp)
    sw $s2, 8($sp)
    sw $s3, 12($sp)
    sw $s4, 16($sp)
    sw $s5, 20($sp)
    sw $s6, 24($sp)
    sw $s7, 28($sp)
    la $t0, this
    lw $t0, 0($t0)
    # getprop x -> t2
    lw $t1, 0($t0)
    la $t0, this
    lw $t0, 0($t0)
    # getprop y -> t3
    lw $t2, 4($t0)
    move $t1, $t1
    move $t2, $t2
    add $t0, $t1, $t2
    move $t0, $t0
    move $v0, $t0
Point.sum_epilog:
    # ---- EPILOG ----
    lw $s0, 0($sp)
    lw $s1, 4($sp)
    lw $s2, 8($sp)
    lw $s3, 12($sp)
    lw $s4, 16($sp)
    lw $s5, 20($sp)
    lw $s6, 24($sp)
    lw $s7, 28($sp)
    addi $sp, $sp, 32
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    beq $ra, $zero, __program_exit
    jr $ra
    j Point.sum_epilog
main:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    addi $sp, $sp, -32
    sw $s0, 0($sp)
    sw $s1, 4($sp)
    sw $s2, 8($sp)
    sw $s3, 12($sp)
    sw $s4, 16($sp)
    sw $s5, 20($sp)
    sw $s6, 24($sp)
    sw $s7, 28($sp)
    # alloc_array size=5
    li $a0, 24
    li $v0, 9
    syscall
    move $t0, $v0
    li $t9, 5
    sw $t9, 0($t0)
    li $t1, 10
    move $t9, $t1
    # setidx t1[0] = t3
    lw $t7, 0($t0)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t1_0_1
    sw $t9, 4($t0)
    j setidx_done_t1_0_1
setidx_oob_t1_0_1:
    # índice fuera de rango, se ignora
setidx_done_t1_0_1:
    li $t1, 20
    move $t9, $t1
    # setidx t1[1] = t3
    lw $t7, 0($t0)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t1_1_2
    sw $t9, 8($t0)
    j setidx_done_t1_1_2
setidx_oob_t1_1_2:
    # índice fuera de rango, se ignora
setidx_done_t1_1_2:
    li $t1, 30
    move $t9, $t1
    # setidx t1[2] = t3
    lw $t7, 0($t0)
    li $t6, 2
    bge $t6, $t7, setidx_oob_t1_2_3
    sw $t9, 12($t0)
    j setidx_done_t1_2_3
setidx_oob_t1_2_3:
    # índice fuera de rango, se ignora
setidx_done_t1_2_3:
    li $t1, 40
    move $t9, $t1
    # setidx t1[3] = t3
    lw $t7, 0($t0)
    li $t6, 3
    bge $t6, $t7, setidx_oob_t1_3_4
    sw $t9, 16($t0)
    j setidx_done_t1_3_4
setidx_oob_t1_3_4:
    # índice fuera de rango, se ignora
setidx_done_t1_3_4:
    li $t1, 50
    move $t9, $t1
    # setidx t1[4] = t3
    lw $t7, 0($t0)
    li $t6, 4
    bge $t6, $t7, setidx_oob_t1_4_5
    sw $t9, 20($t0)
    j setidx_done_t1_4_5
setidx_oob_t1_4_5:
    # índice fuera de rango, se ignora
setidx_done_t1_4_5:
    la $t9, g_arr
    sw $t0, 0($t9)
    la $t2, g_arr
    lw $t2, 0($t2)
    li $t1, 0
    # getidx t1[t3] -> t2 (dinámico)
    sll $t6, $t1, 2
    addi $t6, $t6, 4
    lw $t8, 0($t2)
    move $t7, $t1
    bge $t7, $t8, getidx_oob_dyn_t2
    add $t6, $t2, $t6
    lw $t3, 0($t6)
    j getidx_done_t2
getidx_oob_static_t2:
    li $t3, 0
    j getidx_done_t2
getidx_oob_dyn_t2:
    li $t3, 0
getidx_done_t2:
    move $t3, $t3
    move $a0, $t3
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t3, g_arr
    lw $t3, 0($t3)
    li $t1, 2
    # getidx t2[t3] -> t1 (dinámico)
    sll $t6, $t1, 2
    addi $t6, $t6, 4
    lw $t8, 0($t3)
    move $t7, $t1
    bge $t7, $t8, getidx_oob_dyn_t1
    add $t6, $t3, $t6
    lw $t2, 0($t6)
    j getidx_done_t1
getidx_oob_static_t1:
    li $t2, 0
    j getidx_done_t1
getidx_oob_dyn_t1:
    li $t2, 0
getidx_done_t1:
    move $t2, $t2
    move $a0, $t2
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t2, 99
    la $t1, g_arr
    lw $t1, 0($t1)
    li $t3, 1
    move $t9, $t2
    # setidx t3[t2] = t1 (dinámico)
    lw $t7, 0($t1)
    bge $t3, $t7, setidx_oob_dyn_t3_6
    sll $t6, $t3, 2
    addi $t6, $t6, 4
    add $t6, $t1, $t6
    sw $t9, 0($t6)
    j setidx_done_dyn_t3_6
setidx_oob_dyn_t3_6:
    # índice fuera de rango (dinámico), se ignora
setidx_done_dyn_t3_6:
    la $t2, g_arr
    lw $t2, 0($t2)
    li $t3, 1
    # getidx t1[t2] -> t3 (dinámico)
    sll $t6, $t3, 2
    addi $t6, $t6, 4
    lw $t8, 0($t2)
    move $t7, $t3
    bge $t7, $t8, getidx_oob_dyn_t3
    add $t6, $t2, $t6
    lw $t1, 0($t6)
    j getidx_done_t3
getidx_oob_static_t3:
    li $t1, 0
    j getidx_done_t3
getidx_oob_dyn_t3:
    li $t1, 0
getidx_done_t3:
    move $t1, $t1
    move $a0, $t1
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # newobj Point -> t3
    li $a0, 8
    li $v0, 9
    syscall
    move $t1, $v0
    la $t9, g_p1
    sw $t1, 0($t9)
    li $t4, 5
    la $t3, g_p1
    lw $t3, 0($t3)
    move $t4, $t4
    # setprop x
    sw $t4, 0($t3)
    li $t4, 10
    la $t3, g_p1
    lw $t3, 0($t3)
    move $t4, $t4
    # setprop y
    sw $t4, 4($t3)
    la $t4, g_p1
    lw $t4, 0($t4)
    # getprop x -> t2
    lw $t3, 0($t4)
    move $t3, $t3
    move $a0, $t3
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t3, 100
    li $t4, 200
    la $t2, g_p1
    lw $t2, 0($t2)
    move $t2, $t2
    addi $sp, $sp, -4
    sw $t2, 0($sp)
    move $t3, $t3
    addi $sp, $sp, -4
    sw $t3, 0($sp)
    move $t4, $t4
    addi $sp, $sp, -4
    sw $t4, 0($sp)
    move $t2, $t2
    la $t9, this
    sw $t2, 0($t9)
    jal Point.init
    addi $sp, $sp, 12
    move $t4, $v0
    la $t3, g_p1
    lw $t3, 0($t3)
    # getprop x -> t1
    lw $t2, 0($t3)
    move $t2, $t2
    move $a0, $t2
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t2, g_p1
    lw $t2, 0($t2)
    move $t2, $t2
    addi $sp, $sp, -4
    sw $t2, 0($sp)
    move $t2, $t2
    la $t9, this
    sw $t2, 0($t9)
    jal Point.sum
    addi $sp, $sp, 4
    move $t2, $v0
    move $t2, $t2
    la $t9, g_total
    sw $t2, 0($t9)
    la $t0, g_total
    lw $a0, 0($t0)
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $v0, 10
    syscall