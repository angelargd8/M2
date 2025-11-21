

# ===== Compiscript Program =====

.data
this: .word 0
g_PI: .word 314
g_greeting: .word str_3
g_flag: .word 0
g_numbers: .word 1, 2, 3, 4, 5
g_matrix_row_0: .word 1, 2
g_matrix_row_1: .word 3, 4
g_matrix: .word g_matrix_row_0, g_matrix_row_1
exc_handler: .word 0
exc_value: .word 0
str_div_zero: .asciiz "division by zero"
str_0: .asciiz "Hello world"
str_1: .asciiz "Hello"
str_2: .asciiz "Compiscript concat"
str_3: .asciiz "Hello, Compiscript!"
str_4: .asciiz "test"
nl: .asciiz "\n"
str_lbr: .asciiz "["
str_rbr: .asciiz "]"
str_comma: .asciiz ", "
str_array: .asciiz "[array]"

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
    # print string (literal/global): str_0
    la $a0, str_0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t0, 1
    move $t0, $t0
    move $a0, $t0
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t1, str_1
    la $t2, str_2
    li $a0, 512
    li $v0, 9
    syscall
    move $t3, $v0
    move $t4, $t3
concat_copy_a_t3_1:
    lb $t5, 0($t1)
    sb $t5, 0($t4)
    beq $t5, $zero, concat_copy_b_t3_1
    addi $t1, $t1, 1
    addi $t4, $t4, 1
    j concat_copy_a_t3_1
concat_copy_b_t3_1:
    lb $t5, 0($t2)
    sb $t5, 0($t4)
    beq $t5, $zero, concat_done_t3_1
    addi $t2, $t2, 1
    addi $t4, $t4, 1
    j concat_copy_b_t3_1
concat_done_t3_1:
    sb $zero, 0($t4)
    move $t6, $t3
    # print dynamic string in t3
    move $a0, $t6
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t6, 314
    move $t6, $t6
    la $t9, g_PI
    sw $t6, 0($t9)
    la $t6, str_3
    la $t9, g_greeting
    sw $t6, 0($t9)
    # alloc_array size=5
    li $a0, 24
    li $v0, 9
    syscall
    move $t6, $v0
    li $t9, 5
    sw $t9, 0($t6)
    li $t7, 1
    move $t8, $t7
    # setidx t3[0] = t2
    lw $t9, 0($t6)
    li $t7, 0
    bge $t7, $t9, setidx_oob_t3_0_1
    sw $t8, 4($t6)
    j setidx_done_t3_0_1
setidx_oob_t3_0_1:
    # índice fuera de rango, se ignora
setidx_done_t3_0_1:
    li $t7, 2
    move $t8, $t7
    # setidx t3[1] = t2
    lw $t9, 0($t6)
    li $t7, 1
    bge $t7, $t9, setidx_oob_t3_1_2
    sw $t8, 8($t6)
    j setidx_done_t3_1_2
setidx_oob_t3_1_2:
    # índice fuera de rango, se ignora
setidx_done_t3_1_2:
    li $t7, 3
    move $t8, $t7
    # setidx t3[2] = t2
    lw $t9, 0($t6)
    li $t7, 2
    bge $t7, $t9, setidx_oob_t3_2_3
    sw $t8, 12($t6)
    j setidx_done_t3_2_3
setidx_oob_t3_2_3:
    # índice fuera de rango, se ignora
setidx_done_t3_2_3:
    li $t7, 4
    move $t8, $t7
    # setidx t3[3] = t2
    lw $t9, 0($t6)
    li $t7, 3
    bge $t7, $t9, setidx_oob_t3_3_4
    sw $t8, 16($t6)
    j setidx_done_t3_3_4
setidx_oob_t3_3_4:
    # índice fuera de rango, se ignora
setidx_done_t3_3_4:
    li $t7, 5
    move $t8, $t7
    # setidx t3[4] = t2
    lw $t9, 0($t6)
    li $t7, 4
    bge $t7, $t9, setidx_oob_t3_4_5
    sw $t8, 20($t6)
    j setidx_done_t3_4_5
setidx_oob_t3_4_5:
    # índice fuera de rango, se ignora
setidx_done_t3_4_5:
    la $t9, g_numbers
    sw $t6, 0($t9)
    # alloc_array size=2
    li $a0, 12
    li $v0, 9
    syscall
    move $t8, $v0
    li $t9, 2
    sw $t9, 0($t8)
    # alloc_array size=2
    li $a0, 12
    li $v0, 9
    syscall
    move $t7, $v0
    li $t9, 2
    sw $t9, 0($t7)
    li $t0, 1
    move $t8, $t0
    # setidx t2[0] = t1
    lw $t9, 0($t7)
    li $t7, 0
    bge $t7, $t9, setidx_oob_t2_0_6
    sw $t8, 4($t7)
    j setidx_done_t2_0_6
setidx_oob_t2_0_6:
    # índice fuera de rango, se ignora
setidx_done_t2_0_6:
    li $t0, 2
    move $t8, $t0
    # setidx t2[1] = t1
    lw $t9, 0($t7)
    li $t7, 1
    bge $t7, $t9, setidx_oob_t2_1_7
    sw $t8, 8($t7)
    j setidx_done_t2_1_7
setidx_oob_t2_1_7:
    # índice fuera de rango, se ignora
setidx_done_t2_1_7:
    move $t8, $t7
    # setidx t3[0] = t2
    lw $t9, 0($t8)
    li $t7, 0
    bge $t7, $t9, setidx_oob_t3_0_8
    sw $t8, 4($t8)
    j setidx_done_t3_0_8
setidx_oob_t3_0_8:
    # índice fuera de rango, se ignora
setidx_done_t3_0_8:
    # alloc_array size=2
    li $a0, 12
    li $v0, 9
    syscall
    move $t7, $v0
    li $t9, 2
    sw $t9, 0($t7)
    li $t0, 3
    move $t8, $t0
    # setidx t2[0] = t1
    lw $t9, 0($t7)
    li $t7, 0
    bge $t7, $t9, setidx_oob_t2_0_9
    sw $t8, 4($t7)
    j setidx_done_t2_0_9
setidx_oob_t2_0_9:
    # índice fuera de rango, se ignora
setidx_done_t2_0_9:
    li $t0, 4
    move $t8, $t0
    # setidx t2[1] = t1
    lw $t9, 0($t7)
    li $t7, 1
    bge $t7, $t9, setidx_oob_t2_1_10
    sw $t8, 8($t7)
    j setidx_done_t2_1_10
setidx_oob_t2_1_10:
    # índice fuera de rango, se ignora
setidx_done_t2_1_10:
    move $t8, $t7
    # setidx t3[1] = t2
    lw $t9, 0($t8)
    li $t7, 1
    bge $t7, $t9, setidx_oob_t3_1_11
    sw $t8, 8($t8)
    j setidx_done_t3_1_11
setidx_oob_t3_1_11:
    # índice fuera de rango, se ignora
setidx_done_t3_1_11:
    la $t9, g_matrix
    sw $t8, 0($t9)
    la $t0, g_PI
    lw $a0, 0($t0)
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, g_greeting
    lw $a0, 0($t0)
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, g_flag
    lw $a0, 0($t0)
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print 1D global array numbers
    li $a0, 91
    li $v0, 11
    syscall
    li $a0, 1
    li $v0, 1
    syscall
    li $a0, 44
    li $v0, 11
    syscall
    li $a0, 32
    li $v0, 11
    syscall
    li $a0, 2
    li $v0, 1
    syscall
    li $a0, 44
    li $v0, 11
    syscall
    li $a0, 32
    li $v0, 11
    syscall
    li $a0, 3
    li $v0, 1
    syscall
    li $a0, 44
    li $v0, 11
    syscall
    li $a0, 32
    li $v0, 11
    syscall
    li $a0, 4
    li $v0, 1
    syscall
    li $a0, 44
    li $v0, 11
    syscall
    li $a0, 32
    li $v0, 11
    syscall
    li $a0, 5
    li $v0, 1
    syscall
    li $a0, 93
    li $v0, 11
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print 2D global array matrix
    li $a0, 91
    li $v0, 11
    syscall
    li $a0, 91
    li $v0, 11
    syscall
    li $a0, 1
    li $v0, 1
    syscall
    li $a0, 44
    li $v0, 11
    syscall
    li $a0, 32
    li $v0, 11
    syscall
    li $a0, 2
    li $v0, 1
    syscall
    li $a0, 93
    li $v0, 11
    syscall
    li $a0, 44
    li $v0, 11
    syscall
    li $a0, 32
    li $v0, 11
    syscall
    li $a0, 91
    li $v0, 11
    syscall
    li $a0, 3
    li $v0, 1
    syscall
    li $a0, 44
    li $v0, 11
    syscall
    li $a0, 32
    li $v0, 11
    syscall
    li $a0, 4
    li $v0, 1
    syscall
    li $a0, 93
    li $v0, 11
    syscall
    li $a0, 93
    li $v0, 11
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print string (literal/global): str_4
    la $a0, str_4
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $v0, 10
    syscall