

# ===== Compiscript Program =====

.data
this: .word 0
g_PI: .word 314
g_greeting: .word str_0
g_flag: .word 0
g_numbers: .word 1, 2, 3, 4, 5
g_matrix_row_0: .word 1, 2
g_matrix_row_1: .word 3, 4
g_matrix: .word g_matrix_row_0, g_matrix_row_1
g_addFive: .word 0
exc_handler: .word 0
exc_value: .word 0
str_div_zero: .asciiz "division by zero"
str_0: .asciiz "Hello, Compiscript!"
str_1: .asciiz "5 + 1 = "
str_2: .asciiz "Greater than 5"
str_3: .asciiz "5 or less"
str_4: .asciiz "Result is now "
str_5: .asciiz "Loop index: "
str_6: .asciiz "Number: "
str_7: .asciiz "It's seven"
str_8: .asciiz "It's six"
str_9: .asciiz "Something else"
str_10: .asciiz "Risky access: "
str_11: .asciiz "Caught an error: "
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

makeAdder:
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
    li $t1, 1
    move $t0, $t0
    move $t1, $t1
    add $t2, $t0, $t1
    move $t2, $t2
    move $v0, $t2
makeAdder_epilog:
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
    j makeAdder_epilog
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
    li $t0, 314
    move $t0, $t0
    la $t9, g_PI
    sw $t0, 0($t9)
    la $t0, str_0
    la $t9, g_greeting
    sw $t0, 0($t9)
    # alloc_array size=5
    li $a0, 24
    li $v0, 9
    syscall
    move $t0, $v0
    li $t9, 5
    sw $t9, 0($t0)
    li $t1, 1
    move $t9, $t1
    # setidx t3[0] = t2
    lw $t7, 0($t0)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t3_0_1
    sw $t9, 4($t0)
    j setidx_done_t3_0_1
setidx_oob_t3_0_1:
    # índice fuera de rango, se ignora
setidx_done_t3_0_1:
    li $t1, 2
    move $t9, $t1
    # setidx t3[1] = t2
    lw $t7, 0($t0)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t3_1_2
    sw $t9, 8($t0)
    j setidx_done_t3_1_2
setidx_oob_t3_1_2:
    # índice fuera de rango, se ignora
setidx_done_t3_1_2:
    li $t1, 3
    move $t9, $t1
    # setidx t3[2] = t2
    lw $t7, 0($t0)
    li $t6, 2
    bge $t6, $t7, setidx_oob_t3_2_3
    sw $t9, 12($t0)
    j setidx_done_t3_2_3
setidx_oob_t3_2_3:
    # índice fuera de rango, se ignora
setidx_done_t3_2_3:
    li $t1, 4
    move $t9, $t1
    # setidx t3[3] = t2
    lw $t7, 0($t0)
    li $t6, 3
    bge $t6, $t7, setidx_oob_t3_3_4
    sw $t9, 16($t0)
    j setidx_done_t3_3_4
setidx_oob_t3_3_4:
    # índice fuera de rango, se ignora
setidx_done_t3_3_4:
    li $t1, 5
    move $t9, $t1
    # setidx t3[4] = t2
    lw $t7, 0($t0)
    li $t6, 4
    bge $t6, $t7, setidx_oob_t3_4_5
    sw $t9, 20($t0)
    j setidx_done_t3_4_5
setidx_oob_t3_4_5:
    # índice fuera de rango, se ignora
setidx_done_t3_4_5:
    la $t9, g_numbers
    sw $t0, 0($t9)
    # alloc_array size=2
    li $a0, 12
    li $v0, 9
    syscall
    move $t2, $v0
    li $t9, 2
    sw $t9, 0($t2)
    # alloc_array size=2
    li $a0, 12
    li $v0, 9
    syscall
    move $t1, $v0
    li $t9, 2
    sw $t9, 0($t1)
    li $t3, 1
    move $t9, $t3
    # setidx t2[0] = t1
    lw $t7, 0($t1)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t2_0_6
    sw $t9, 4($t1)
    j setidx_done_t2_0_6
setidx_oob_t2_0_6:
    # índice fuera de rango, se ignora
setidx_done_t2_0_6:
    li $t3, 2
    move $t9, $t3
    # setidx t2[1] = t1
    lw $t7, 0($t1)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t2_1_7
    sw $t9, 8($t1)
    j setidx_done_t2_1_7
setidx_oob_t2_1_7:
    # índice fuera de rango, se ignora
setidx_done_t2_1_7:
    move $t9, $t1
    # setidx t3[0] = t2
    lw $t7, 0($t2)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t3_0_8
    sw $t9, 4($t2)
    j setidx_done_t3_0_8
setidx_oob_t3_0_8:
    # índice fuera de rango, se ignora
setidx_done_t3_0_8:
    # alloc_array size=2
    li $a0, 12
    li $v0, 9
    syscall
    move $t1, $v0
    li $t9, 2
    sw $t9, 0($t1)
    li $t3, 3
    move $t9, $t3
    # setidx t2[0] = t1
    lw $t7, 0($t1)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t2_0_9
    sw $t9, 4($t1)
    j setidx_done_t2_0_9
setidx_oob_t2_0_9:
    # índice fuera de rango, se ignora
setidx_done_t2_0_9:
    li $t3, 4
    move $t9, $t3
    # setidx t2[1] = t1
    lw $t7, 0($t1)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t2_1_10
    sw $t9, 8($t1)
    j setidx_done_t2_1_10
setidx_oob_t2_1_10:
    # índice fuera de rango, se ignora
setidx_done_t2_1_10:
    move $t9, $t1
    # setidx t3[1] = t2
    lw $t7, 0($t2)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t3_1_11
    sw $t9, 8($t2)
    j setidx_done_t3_1_11
setidx_oob_t3_1_11:
    # índice fuera de rango, se ignora
setidx_done_t3_1_11:
    la $t9, g_matrix
    sw $t2, 0($t9)
    li $t4, 5
    move $t4, $t4
    addi $sp, $sp, -4
    sw $t4, 0($sp)
    jal makeAdder
    addi $sp, $sp, 4
    move $t4, $v0
    la $t9, g_addFive
    sw $t4, 0($t9)
    la $t1, g_addFive
    lw $t1, 0($t1)
    move $t1, $t1
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $t1
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $t3, $v0
    la $t5, str_1
    move $t6, $t3
    li $a0, 512
    li $v0, 9
    syscall
    move $t7, $v0
    move $t8, $t7
concat_copy_a_t1_1:
    lb $t9, 0($t5)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_copy_b_t1_1
    addi $t5, $t5, 1
    addi $t8, $t8, 1
    j concat_copy_a_t1_1
concat_copy_b_t1_1:
    lb $t9, 0($t6)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_done_t1_1
    addi $t6, $t6, 1
    addi $t8, $t8, 1
    j concat_copy_b_t1_1
concat_done_t1_1:
    sb $zero, 0($t8)
    move $t3, $t7
    # print dynamic string in t1
    move $a0, $t3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t3, g_addFive
    lw $t3, 0($t3)
    li $t1, 5
    move $t3, $t3
    move $t1, $t1
    sgt $s0, $t3, $t1
    move $s0, $s0
    beq $s0, $zero, L1
    # print string (literal/global): str_2
    la $a0, str_2
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    j L2
L1:
    # print string (literal/global): str_3
    la $a0, str_3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L2:
L3:
    la $s0, g_addFive
    lw $s0, 0($s0)
    li $t1, 10
    move $s0, $s0
    move $t1, $t1
    slt $t3, $s0, $t1
    move $t3, $t3
    beq $t3, $zero, L4
    la $t3, g_addFive
    lw $t3, 0($t3)
    li $t1, 1
    move $t3, $t3
    move $t1, $t1
    add $s0, $t3, $t1
    move $s0, $s0
    la $t9, g_addFive
    sw $s0, 0($t9)
    j L3
L4:
L5:
    la $t1, g_addFive
    lw $t1, 0($t1)
    move $t1, $t1
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $t1
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $t3, $v0
    la $s1, str_4
    move $s2, $t3
    li $a0, 512
    li $v0, 9
    syscall
    move $s3, $v0
    move $s4, $s3
concat_copy_a_t1_2:
    lb $s5, 0($s1)
    sb $s5, 0($s4)
    beq $s5, $zero, concat_copy_b_t1_2
    addi $s1, $s1, 1
    addi $s4, $s4, 1
    j concat_copy_a_t1_2
concat_copy_b_t1_2:
    lb $s5, 0($s2)
    sb $s5, 0($s4)
    beq $s5, $zero, concat_done_t1_2
    addi $s2, $s2, 1
    addi $s4, $s4, 1
    j concat_copy_b_t1_2
concat_done_t1_2:
    sb $zero, 0($s4)
    move $t3, $s3
    # print dynamic string in t1
    move $a0, $t3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t3, g_addFive
    lw $t3, 0($t3)
    li $t1, 1
    move $t3, $t3
    move $t1, $t1
    sub $s0, $t3, $t1
    move $s0, $s0
    la $t9, g_addFive
    sw $s0, 0($t9)
    la $s0, g_addFive
    lw $s0, 0($s0)
    li $t1, 7
    move $s0, $s0
    move $t1, $t1
    sgt $t3, $s0, $t1
    move $t3, $t3
    bne $t3, $zero, L5
L6:
    li $t3, 0
    move $t1, $t3
L7:
    li $t3, 3
    move $t1, $t1
    move $t3, $t3
    slt $s0, $t1, $t3
    move $s0, $s0
    beq $s0, $zero, L8
    move $t1, $t1
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $t1
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $t3, $v0
    la $s6, str_5
    move $s7, $t3
    li $a0, 512
    li $v0, 9
    syscall
    move $t0, $v0
    move $t2, $t0
concat_copy_a_t1_3:
    lb $t4, 0($s6)
    sb $t4, 0($t2)
    beq $t4, $zero, concat_copy_b_t1_3
    addi $s6, $s6, 1
    addi $t2, $t2, 1
    j concat_copy_a_t1_3
concat_copy_b_t1_3:
    lb $t4, 0($s7)
    sb $t4, 0($t2)
    beq $t4, $zero, concat_done_t1_3
    addi $s7, $s7, 1
    addi $t2, $t2, 1
    j concat_copy_b_t1_3
concat_done_t1_3:
    sb $zero, 0($t2)
    move $t3, $t0
    # print dynamic string in t1
    move $a0, $t3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L9:
    li $t3, 1
    move $t1, $t1
    move $t3, $t3
    add $s0, $t1, $t3
    move $t1, $s0
    j L7
L8:
    la $s0, g_numbers
    lw $s0, 0($s0)
    li $t3, 0
    # array_length t3 -> t4
    lw $a0, 0($s0)
L10:
    move $t3, $t3
    move $a0, $a0
    slt $a1, $t3, $a0
    move $a1, $a1
    beq $a1, $zero, L11
    # getidx t3[t1] -> t6 (dinámico)
    sll $t6, $t3, 2
    addi $t6, $t6, 4
    lw $t8, 0($s0)
    move $t7, $t3
    bge $t7, $t8, getidx_oob_dyn_t6
    add $t6, $s0, $t6
    lw $a2, 0($t6)
    j getidx_done_t6
getidx_oob_static_t6:
    li $a2, 0
    j getidx_done_t6
getidx_oob_dyn_t6:
    li $a2, 0
getidx_done_t6:
    move $a3, $a2
    li $t5, 3
    move $a3, $a3
    move $t5, $t5
    xor $t6, $a3, $t5
    sltiu $t6, $t6, 1
    move $t6, $t6
    beq $t6, $zero, L13
    j L12
L13:
    move $a3, $a3
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $a3
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $t5, $v0
    la $t7, str_6
    move $t8, $t5
    li $a0, 512
    li $v0, 9
    syscall
    move $t9, $v0
    move $s1, $t9
concat_copy_a_t8_4:
    lb $s2, 0($t7)
    sb $s2, 0($s1)
    beq $s2, $zero, concat_copy_b_t8_4
    addi $t7, $t7, 1
    addi $s1, $s1, 1
    j concat_copy_a_t8_4
concat_copy_b_t8_4:
    lb $s2, 0($t8)
    sb $s2, 0($s1)
    beq $s2, $zero, concat_done_t8_4
    addi $t8, $t8, 1
    addi $s1, $s1, 1
    j concat_copy_b_t8_4
concat_done_t8_4:
    sb $zero, 0($s1)
    move $t5, $t9
    # print dynamic string in t8
    move $a0, $t5
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t5, 4
    move $a3, $a3
    move $t5, $t5
    sgt $t6, $a3, $t5
    move $t6, $t6
    beq $t6, $zero, L15
    j L11
L15:
L12:
    li $t6, 1
    move $t3, $t3
    move $t6, $t6
    add $t5, $t3, $t6
    move $t3, $t5
    j L10
L11:
    la $s0, g_addFive
    lw $s0, 0($s0)
    move $s0, $s0
    li $s3, 7
    xor $s4, $s0, $s3
    sltiu $s4, $s4, 1
    move $s4, $s4
    bne $s4, $zero, L18
    move $s0, $s0
    li $s5, 6
    xor $s6, $s0, $s5
    sltiu $s6, $s6, 1
    move $s6, $s6
    bne $s6, $zero, L19
    j L20
L18:
    # print string (literal/global): str_7
    la $a0, str_7
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L19:
    # print string (literal/global): str_8
    la $a0, str_8
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L20:
    # print string (literal/global): str_9
    la $a0, str_9
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L17:
    # push_handler L21
    la $t9, exc_handler
    la $t8, L21
    sw $t8, 0($t9)
    la $s0, g_numbers
    lw $s0, 0($s0)
    li $s7, 10
    # getidx t3[t14] -> t15 (dinámico)
    sll $t6, $s7, 2
    addi $t6, $t6, 4
    lw $t8, 0($s0)
    move $t7, $s7
    bge $t7, $t8, getidx_oob_dyn_t15
    add $t6, $s0, $t6
    lw $t0, 0($t6)
    j getidx_done_t15
getidx_oob_static_t15:
    li $t0, 0
    j getidx_done_t15
getidx_oob_dyn_t15:
    li $t0, 0
getidx_done_t15:
    move $s7, $t0
    move $s7, $s7
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $s7
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $s0, $v0
    la $t2, str_10
    move $t4, $s0
    li $a0, 512
    li $v0, 9
    syscall
    move $t7, $v0
    move $t8, $t7
concat_copy_a_t3_5:
    lb $t9, 0($t2)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_copy_b_t3_5
    addi $t2, $t2, 1
    addi $t8, $t8, 1
    j concat_copy_a_t3_5
concat_copy_b_t3_5:
    lb $t9, 0($t4)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_done_t3_5
    addi $t4, $t4, 1
    addi $t8, $t8, 1
    j concat_copy_b_t3_5
concat_done_t3_5:
    sb $zero, 0($t8)
    move $s0, $t7
    # print dynamic string in t3
    move $a0, $s0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # pop_handler
    la $t9, exc_handler
    sw $zero, 0($t9)
    la $t9, exc_value
    sw $zero, 0($t9)
    j L22
L21:
    # get_exception
    la $t9, exc_value
    lw $s0, 0($t9)
    la $s1, str_11
    move $s2, $s0
    li $a0, 512
    li $v0, 9
    syscall
    move $s3, $v0
    move $s4, $s3
concat_copy_a_t17_6:
    lb $s5, 0($s1)
    sb $s5, 0($s4)
    beq $s5, $zero, concat_copy_b_t17_6
    addi $s1, $s1, 1
    addi $s4, $s4, 1
    j concat_copy_a_t17_6
concat_copy_b_t17_6:
    lb $s5, 0($s2)
    sb $s5, 0($s4)
    beq $s5, $zero, concat_done_t17_6
    addi $s2, $s2, 1
    addi $s4, $s4, 1
    j concat_copy_b_t17_6
concat_done_t17_6:
    sb $zero, 0($s4)
    move $a0, $s3
    # print dynamic string in t17
    move $a0, $a0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L22:
    li $v0, 10
    syscall