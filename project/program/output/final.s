

# ===== Compiscript Program =====

.data
this: .word 0
g_PI: .word 314
g_greeting: .word str_2
g_flag: .word 0
g_numbers: .word 1, 2, 3, 4, 5
g_matrix_row_0: .word 1, 2
g_matrix_row_1: .word 3, 4
g_matrix: .word g_matrix_row_0, g_matrix_row_1
g_addFive: .word 0
g_dog: .word 0
g_first: .word 0
g_multiples: .word 0
exc_handler: .word 0
exc_value: .word 0
str_div_zero: .asciiz "division by zero"
str_0: .asciiz " makes a sound."
str_1: .asciiz " barks."
str_2: .asciiz "Hello, Compiscript!"
str_3: .asciiz "5 + 1 = "
str_4: .asciiz "Greater than 5"
str_5: .asciiz "5 or less"
str_6: .asciiz "Result is now "
str_7: .asciiz "Loop index: "
str_8: .asciiz "Number: "
str_9: .asciiz "It's seven"
str_10: .asciiz "It's six"
str_11: .asciiz "Something else"
str_12: .asciiz "Risky access: "
str_13: .asciiz "Caught an error: "
str_14: .asciiz "Rex"
str_15: .asciiz "First number: "
str_16: .asciiz "Multiples of 2: "
str_17: .asciiz ","
str_18: .asciiz "Program finished."
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
Animal.constructor:
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
    move $t1, $t1
    move $t0, $t0
    # setprop name
    sw $t0, 0($t1)
Animal.constructor_epilog:
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
Animal.speak:
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
    move $t0, $t0
    # getprop name -> t2
    lw $t1, 0($t0)
    move $t2, $t1
    la $t3, str_0
    li $a0, 512
    li $v0, 9
    syscall
    move $t4, $v0
    move $t5, $t4
concat_copy_a_t1_1:
    lb $t6, 0($t2)
    sb $t6, 0($t5)
    beq $t6, $zero, concat_copy_b_t1_1
    addi $t2, $t2, 1
    addi $t5, $t5, 1
    j concat_copy_a_t1_1
concat_copy_b_t1_1:
    lb $t6, 0($t3)
    sb $t6, 0($t5)
    beq $t6, $zero, concat_done_t1_1
    addi $t3, $t3, 1
    addi $t5, $t5, 1
    j concat_copy_b_t1_1
concat_done_t1_1:
    sb $zero, 0($t5)
    move $t7, $t4
    move $t7, $t7
    move $v0, $t7
Animal.speak_epilog:
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
    j Animal.speak_epilog
Dog.speak:
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
    move $t0, $t0
    # getprop name -> t3
    lw $t1, 0($t0)
    move $t2, $t1
    la $t3, str_1
    li $a0, 512
    li $v0, 9
    syscall
    move $t4, $v0
    move $t5, $t4
concat_copy_a_t2_2:
    lb $t6, 0($t2)
    sb $t6, 0($t5)
    beq $t6, $zero, concat_copy_b_t2_2
    addi $t2, $t2, 1
    addi $t5, $t5, 1
    j concat_copy_a_t2_2
concat_copy_b_t2_2:
    lb $t6, 0($t3)
    sb $t6, 0($t5)
    beq $t6, $zero, concat_done_t2_2
    addi $t3, $t3, 1
    addi $t5, $t5, 1
    j concat_copy_b_t2_2
concat_done_t2_2:
    sb $zero, 0($t5)
    move $t7, $t4
    move $t7, $t7
    move $v0, $t7
Dog.speak_epilog:
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
    j Dog.speak_epilog
getMultiples:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    addi $sp, $sp, -16
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
    lw $t1, 8($fp)
    li $t2, 1
    move $t1, $t1
    move $t2, $t2
    mul $t3, $t1, $t2
    move $t9, $t3
    # setidx t2[0] = t4
    lw $t7, 0($t0)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t2_0_1
    sw $t9, 4($t0)
    j setidx_done_t2_0_1
setidx_oob_t2_0_1:
    # índice fuera de rango, se ignora
setidx_done_t2_0_1:
    lw $t3, 8($fp)
    li $t2, 2
    move $t3, $t3
    move $t2, $t2
    mul $t1, $t3, $t2
    move $t9, $t1
    # setidx t2[1] = t1
    lw $t7, 0($t0)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t2_1_2
    sw $t9, 8($t0)
    j setidx_done_t2_1_2
setidx_oob_t2_1_2:
    # índice fuera de rango, se ignora
setidx_done_t2_1_2:
    lw $t1, 8($fp)
    li $t2, 3
    move $t1, $t1
    move $t2, $t2
    mul $t3, $t1, $t2
    move $t9, $t3
    # setidx t2[2] = t4
    lw $t7, 0($t0)
    li $t6, 2
    bge $t6, $t7, setidx_oob_t2_2_3
    sw $t9, 12($t0)
    j setidx_done_t2_2_3
setidx_oob_t2_2_3:
    # índice fuera de rango, se ignora
setidx_done_t2_2_3:
    lw $t3, 8($fp)
    li $t2, 4
    move $t3, $t3
    move $t2, $t2
    mul $t1, $t3, $t2
    move $t9, $t1
    # setidx t2[3] = t1
    lw $t7, 0($t0)
    li $t6, 3
    bge $t6, $t7, setidx_oob_t2_3_4
    sw $t9, 16($t0)
    j setidx_done_t2_3_4
setidx_oob_t2_3_4:
    # índice fuera de rango, se ignora
setidx_done_t2_3_4:
    lw $t1, 8($fp)
    li $t2, 5
    move $t1, $t1
    move $t2, $t2
    mul $t3, $t1, $t2
    move $t9, $t3
    # setidx t2[4] = t4
    lw $t7, 0($t0)
    li $t6, 4
    bge $t6, $t7, setidx_oob_t2_4_5
    sw $t9, 20($t0)
    j setidx_done_t2_4_5
setidx_oob_t2_4_5:
    # índice fuera de rango, se ignora
setidx_done_t2_4_5:
    move $t0, $t0
    sw $t0, -4($fp)
    lw $t0, -4($fp)
    move $t0, $t0
    move $v0, $t0
getMultiples_epilog:
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
    addi $sp, $sp, 16
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    beq $ra, $zero, __program_exit
    jr $ra
    j getMultiples_epilog
factorial:
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
    sle $t2, $t0, $t1
    move $t2, $t2
    beq $t2, $zero, L1
    li $t2, 1
    move $t2, $t2
    move $v0, $t2
factorial_epilog:
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
L1:
    lw $t2, 8($fp)
    lw $t1, 8($fp)
    li $t0, 1
    move $t1, $t1
    move $t0, $t0
    sub $t3, $t1, $t0
    move $t3, $t3
    addi $sp, $sp, -4
    sw $t3, 0($sp)
    jal factorial
    addi $sp, $sp, 4
    move $t3, $v0
    move $t2, $t2
    move $t3, $t3
    mul $t0, $t2, $t3
    move $t0, $t0
    move $v0, $t0
    j factorial_epilog
    j factorial_epilog
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
    la $t0, str_2
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
    # setidx t2[0] = t1
    lw $t7, 0($t0)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t2_0_6
    sw $t9, 4($t0)
    j setidx_done_t2_0_6
setidx_oob_t2_0_6:
    # índice fuera de rango, se ignora
setidx_done_t2_0_6:
    li $t1, 2
    move $t9, $t1
    # setidx t2[1] = t1
    lw $t7, 0($t0)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t2_1_7
    sw $t9, 8($t0)
    j setidx_done_t2_1_7
setidx_oob_t2_1_7:
    # índice fuera de rango, se ignora
setidx_done_t2_1_7:
    li $t1, 3
    move $t9, $t1
    # setidx t2[2] = t1
    lw $t7, 0($t0)
    li $t6, 2
    bge $t6, $t7, setidx_oob_t2_2_8
    sw $t9, 12($t0)
    j setidx_done_t2_2_8
setidx_oob_t2_2_8:
    # índice fuera de rango, se ignora
setidx_done_t2_2_8:
    li $t1, 4
    move $t9, $t1
    # setidx t2[3] = t1
    lw $t7, 0($t0)
    li $t6, 3
    bge $t6, $t7, setidx_oob_t2_3_9
    sw $t9, 16($t0)
    j setidx_done_t2_3_9
setidx_oob_t2_3_9:
    # índice fuera de rango, se ignora
setidx_done_t2_3_9:
    li $t1, 5
    move $t9, $t1
    # setidx t2[4] = t1
    lw $t7, 0($t0)
    li $t6, 4
    bge $t6, $t7, setidx_oob_t2_4_10
    sw $t9, 20($t0)
    j setidx_done_t2_4_10
setidx_oob_t2_4_10:
    # índice fuera de rango, se ignora
setidx_done_t2_4_10:
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
    # setidx t1[0] = t3
    lw $t7, 0($t1)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t1_0_11
    sw $t9, 4($t1)
    j setidx_done_t1_0_11
setidx_oob_t1_0_11:
    # índice fuera de rango, se ignora
setidx_done_t1_0_11:
    li $t3, 2
    move $t9, $t3
    # setidx t1[1] = t3
    lw $t7, 0($t1)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t1_1_12
    sw $t9, 8($t1)
    j setidx_done_t1_1_12
setidx_oob_t1_1_12:
    # índice fuera de rango, se ignora
setidx_done_t1_1_12:
    move $t9, $t1
    # setidx t2[0] = t1
    lw $t7, 0($t2)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t2_0_13
    sw $t9, 4($t2)
    j setidx_done_t2_0_13
setidx_oob_t2_0_13:
    # índice fuera de rango, se ignora
setidx_done_t2_0_13:
    # alloc_array size=2
    li $a0, 12
    li $v0, 9
    syscall
    move $t1, $v0
    li $t9, 2
    sw $t9, 0($t1)
    li $t3, 3
    move $t9, $t3
    # setidx t1[0] = t3
    lw $t7, 0($t1)
    li $t6, 0
    bge $t6, $t7, setidx_oob_t1_0_14
    sw $t9, 4($t1)
    j setidx_done_t1_0_14
setidx_oob_t1_0_14:
    # índice fuera de rango, se ignora
setidx_done_t1_0_14:
    li $t3, 4
    move $t9, $t3
    # setidx t1[1] = t3
    lw $t7, 0($t1)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t1_1_15
    sw $t9, 8($t1)
    j setidx_done_t1_1_15
setidx_oob_t1_1_15:
    # índice fuera de rango, se ignora
setidx_done_t1_1_15:
    move $t9, $t1
    # setidx t2[1] = t1
    lw $t7, 0($t2)
    li $t6, 1
    bge $t6, $t7, setidx_oob_t2_1_16
    sw $t9, 8($t2)
    j setidx_done_t2_1_16
setidx_oob_t2_1_16:
    # índice fuera de rango, se ignora
setidx_done_t2_1_16:
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
    la $t5, str_3
    move $t6, $t3
    li $a0, 512
    li $v0, 9
    syscall
    move $t7, $v0
    move $t8, $t7
concat_copy_a_t3_3:
    lb $t9, 0($t5)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_copy_b_t3_3
    addi $t5, $t5, 1
    addi $t8, $t8, 1
    j concat_copy_a_t3_3
concat_copy_b_t3_3:
    lb $t9, 0($t6)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_done_t3_3
    addi $t6, $t6, 1
    addi $t8, $t8, 1
    j concat_copy_b_t3_3
concat_done_t3_3:
    sb $zero, 0($t8)
    move $t3, $t7
    # print dynamic string in t3
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
    beq $s0, $zero, L3
    # print string (literal/global): str_4
    la $a0, str_4
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    j L4
L3:
    # print string (literal/global): str_5
    la $a0, str_5
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L4:
L5:
    la $s0, g_addFive
    lw $s0, 0($s0)
    li $t1, 10
    move $s0, $s0
    move $t1, $t1
    slt $t3, $s0, $t1
    move $t3, $t3
    beq $t3, $zero, L6
    la $t3, g_addFive
    lw $t3, 0($t3)
    li $t1, 1
    move $t3, $t3
    move $t1, $t1
    add $s0, $t3, $t1
    move $s0, $s0
    la $t9, g_addFive
    sw $s0, 0($t9)
    j L5
L6:
L7:
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
    la $s1, str_6
    move $s2, $t3
    li $a0, 512
    li $v0, 9
    syscall
    move $s3, $v0
    move $s4, $s3
concat_copy_a_t3_4:
    lb $s5, 0($s1)
    sb $s5, 0($s4)
    beq $s5, $zero, concat_copy_b_t3_4
    addi $s1, $s1, 1
    addi $s4, $s4, 1
    j concat_copy_a_t3_4
concat_copy_b_t3_4:
    lb $s5, 0($s2)
    sb $s5, 0($s4)
    beq $s5, $zero, concat_done_t3_4
    addi $s2, $s2, 1
    addi $s4, $s4, 1
    j concat_copy_b_t3_4
concat_done_t3_4:
    sb $zero, 0($s4)
    move $t3, $s3
    # print dynamic string in t3
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
    bne $t3, $zero, L7
L8:
    li $t3, 0
    move $t1, $t3
L9:
    li $t3, 3
    move $t1, $t1
    move $t3, $t3
    slt $s0, $t1, $t3
    move $s0, $s0
    beq $s0, $zero, L10
    move $t1, $t1
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $t1
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $t3, $v0
    la $s6, str_7
    move $s7, $t3
    li $a0, 512
    li $v0, 9
    syscall
    move $t0, $v0
    move $t2, $t0
concat_copy_a_t3_5:
    lb $t4, 0($s6)
    sb $t4, 0($t2)
    beq $t4, $zero, concat_copy_b_t3_5
    addi $s6, $s6, 1
    addi $t2, $t2, 1
    j concat_copy_a_t3_5
concat_copy_b_t3_5:
    lb $t4, 0($s7)
    sb $t4, 0($t2)
    beq $t4, $zero, concat_done_t3_5
    addi $s7, $s7, 1
    addi $t2, $t2, 1
    j concat_copy_b_t3_5
concat_done_t3_5:
    sb $zero, 0($t2)
    move $t3, $t0
    # print dynamic string in t3
    move $a0, $t3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L11:
    li $t3, 1
    move $t1, $t1
    move $t3, $t3
    add $s0, $t1, $t3
    move $t1, $s0
    j L9
L10:
    la $s0, g_numbers
    lw $s0, 0($s0)
    li $t3, 0
    # array_length t2 -> t4
    lw $a0, 0($s0)
L12:
    move $t3, $t3
    move $a0, $a0
    slt $a1, $t3, $a0
    move $a1, $a1
    beq $a1, $zero, L13
    # getidx t2[t3] -> t6 (dinámico)
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
    beq $t6, $zero, L15
    j L14
L15:
    move $a3, $a3
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $a3
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $t5, $v0
    la $t7, str_8
    move $t8, $t5
    li $a0, 512
    li $v0, 9
    syscall
    move $t9, $v0
    move $s1, $t9
concat_copy_a_t8_6:
    lb $s2, 0($t7)
    sb $s2, 0($s1)
    beq $s2, $zero, concat_copy_b_t8_6
    addi $t7, $t7, 1
    addi $s1, $s1, 1
    j concat_copy_a_t8_6
concat_copy_b_t8_6:
    lb $s2, 0($t8)
    sb $s2, 0($s1)
    beq $s2, $zero, concat_done_t8_6
    addi $t8, $t8, 1
    addi $s1, $s1, 1
    j concat_copy_b_t8_6
concat_done_t8_6:
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
    beq $t6, $zero, L17
    j L13
L17:
L14:
    li $t6, 1
    move $t3, $t3
    move $t6, $t6
    add $t5, $t3, $t6
    move $t3, $t5
    j L12
L13:
    la $s0, g_addFive
    lw $s0, 0($s0)
    move $s0, $s0
    li $s3, 7
    xor $s4, $s0, $s3
    sltiu $s4, $s4, 1
    move $s4, $s4
    bne $s4, $zero, L20
    move $s0, $s0
    li $s5, 6
    xor $s6, $s0, $s5
    sltiu $s6, $s6, 1
    move $s6, $s6
    bne $s6, $zero, L21
    j L22
L20:
    # print string (literal/global): str_9
    la $a0, str_9
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L21:
    # print string (literal/global): str_10
    la $a0, str_10
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L22:
    # print string (literal/global): str_11
    la $a0, str_11
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L19:
    # push_handler L23
    la $t9, exc_handler
    la $t8, L23
    sw $t8, 0($t9)
    la $s0, g_numbers
    lw $s0, 0($s0)
    li $s7, 10
    # getidx t2[t14] -> t15 (dinámico)
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
    la $t2, str_12
    move $t4, $s0
    li $a0, 512
    li $v0, 9
    syscall
    move $t7, $v0
    move $t8, $t7
concat_copy_a_t2_7:
    lb $t9, 0($t2)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_copy_b_t2_7
    addi $t2, $t2, 1
    addi $t8, $t8, 1
    j concat_copy_a_t2_7
concat_copy_b_t2_7:
    lb $t9, 0($t4)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_done_t2_7
    addi $t4, $t4, 1
    addi $t8, $t8, 1
    j concat_copy_b_t2_7
concat_done_t2_7:
    sb $zero, 0($t8)
    move $s0, $t7
    # print dynamic string in t2
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
    j L24
L23:
    # get_exception
    la $t9, exc_value
    lw $s0, 0($t9)
    la $s1, str_13
    move $s2, $s0
    li $a0, 512
    li $v0, 9
    syscall
    move $s3, $v0
    move $s4, $s3
concat_copy_a_t17_8:
    lb $s5, 0($s1)
    sb $s5, 0($s4)
    beq $s5, $zero, concat_copy_b_t17_8
    addi $s1, $s1, 1
    addi $s4, $s4, 1
    j concat_copy_a_t17_8
concat_copy_b_t17_8:
    lb $s5, 0($s2)
    sb $s5, 0($s4)
    beq $s5, $zero, concat_done_t17_8
    addi $s2, $s2, 1
    addi $s4, $s4, 1
    j concat_copy_b_t17_8
concat_done_t17_8:
    sb $zero, 0($s4)
    move $a1, $s3
    # print dynamic string in t17
    move $a0, $a1
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L24:
    # newobj Dog -> t16
    li $a0, 8
    li $v0, 9
    syscall
    move $a2, $v0
    la $a1, str_14
    # setprop name
    sw $a1, 0($a2)
    la $t9, g_dog
    sw $a2, 0($t9)
    la $a3, g_dog
    lw $a3, 0($a3)
    move $a3, $a3
    addi $sp, $sp, -4
    sw $a3, 0($sp)
    move $a3, $a3
    la $t9, this
    sw $a3, 0($t9)
    jal Dog.speak
    move $a3, $v0
    # print dynamic string in t16
    move $a0, $a3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $a3, g_numbers
    lw $a3, 0($a3)
    li $a1, 0
    # getidx t16[t17] -> t18 (dinámico)
    sll $t6, $a1, 2
    addi $t6, $t6, 4
    lw $t8, 0($a3)
    move $t7, $a1
    bge $t7, $t8, getidx_oob_dyn_t18
    add $t6, $a3, $t6
    lw $s6, 0($t6)
    j getidx_done_t18
getidx_oob_static_t18:
    li $s6, 0
    j getidx_done_t18
getidx_oob_dyn_t18:
    li $s6, 0
getidx_done_t18:
    move $s6, $s6
    la $t9, g_first
    sw $s6, 0($t9)
    la $a1, g_first
    lw $a1, 0($a1)
    move $a1, $a1
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $a1
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $a3, $v0
    la $t2, str_15
    move $t4, $a3
    li $a0, 512
    li $v0, 9
    syscall
    move $t7, $v0
    move $t8, $t7
concat_copy_a_t16_9:
    lb $t9, 0($t2)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_copy_b_t16_9
    addi $t2, $t2, 1
    addi $t8, $t8, 1
    j concat_copy_a_t16_9
concat_copy_b_t16_9:
    lb $t9, 0($t4)
    sb $t9, 0($t8)
    beq $t9, $zero, concat_done_t16_9
    addi $t4, $t4, 1
    addi $t8, $t8, 1
    j concat_copy_b_t16_9
concat_done_t16_9:
    sb $zero, 0($t8)
    move $a3, $t7
    # print dynamic string in t16
    move $a0, $a3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $a3, 2
    move $a3, $a3
    addi $sp, $sp, -4
    sw $a3, 0($sp)
    jal getMultiples
    addi $sp, $sp, 4
    move $a3, $v0
    la $t9, g_multiples
    sw $a3, 0($t9)
    la $a1, g_multiples
    lw $a1, 0($a1)
    li $s6, 0
    # getidx t17[t18] -> t19 (dinámico)
    sll $t6, $s6, 2
    addi $t6, $t6, 4
    lw $t8, 0($a1)
    move $t7, $s6
    bge $t7, $t8, getidx_oob_dyn_t19
    add $t6, $a1, $t6
    lw $s1, 0($t6)
    j getidx_done_t19
getidx_oob_static_t19:
    li $s1, 0
    j getidx_done_t19
getidx_oob_dyn_t19:
    li $s1, 0
getidx_done_t19:
    move $s1, $s1
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $s1
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $s6, $v0
    la $s2, str_16
    move $s3, $s6
    li $a0, 512
    li $v0, 9
    syscall
    move $s4, $v0
    move $s5, $s4
concat_copy_a_t18_10:
    lb $t2, 0($s2)
    sb $t2, 0($s5)
    beq $t2, $zero, concat_copy_b_t18_10
    addi $s2, $s2, 1
    addi $s5, $s5, 1
    j concat_copy_a_t18_10
concat_copy_b_t18_10:
    lb $t2, 0($s3)
    sb $t2, 0($s5)
    beq $t2, $zero, concat_done_t18_10
    addi $s3, $s3, 1
    addi $s5, $s5, 1
    j concat_copy_b_t18_10
concat_done_t18_10:
    sb $zero, 0($s5)
    move $s6, $s4
    move $t4, $s6
    la $t7, str_17
    li $a0, 512
    li $v0, 9
    syscall
    move $t8, $v0
    move $t9, $t8
concat_copy_a_t16_11:
    lb $s2, 0($t4)
    sb $s2, 0($t9)
    beq $s2, $zero, concat_copy_b_t16_11
    addi $t4, $t4, 1
    addi $t9, $t9, 1
    j concat_copy_a_t16_11
concat_copy_b_t16_11:
    lb $s2, 0($t7)
    sb $s2, 0($t9)
    beq $s2, $zero, concat_done_t16_11
    addi $t7, $t7, 1
    addi $t9, $t9, 1
    j concat_copy_b_t16_11
concat_done_t16_11:
    sb $zero, 0($t9)
    move $a2, $t8
    la $s1, g_multiples
    lw $s1, 0($s1)
    li $s6, 1
    # getidx t19[t18] -> t17 (dinámico)
    sll $t6, $s6, 2
    addi $t6, $t6, 4
    lw $t8, 0($s1)
    move $t7, $s6
    bge $t7, $t8, getidx_oob_dyn_t17
    add $t6, $s1, $t6
    lw $a1, 0($t6)
    j getidx_done_t17
getidx_oob_static_t17:
    li $a1, 0
    j getidx_done_t17
getidx_oob_dyn_t17:
    li $a1, 0
getidx_done_t17:
    move $a1, $a1
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $a1
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $s6, $v0
    move $s3, $a2
    move $s4, $s6
    li $a0, 512
    li $v0, 9
    syscall
    move $s5, $v0
    move $t2, $s5
concat_copy_a_t18_12:
    lb $t4, 0($s3)
    sb $t4, 0($t2)
    beq $t4, $zero, concat_copy_b_t18_12
    addi $s3, $s3, 1
    addi $t2, $t2, 1
    j concat_copy_a_t18_12
concat_copy_b_t18_12:
    lb $t4, 0($s4)
    sb $t4, 0($t2)
    beq $t4, $zero, concat_done_t18_12
    addi $s4, $s4, 1
    addi $t2, $t2, 1
    j concat_copy_b_t18_12
concat_done_t18_12:
    sb $zero, 0($t2)
    move $s6, $s5
    # print dynamic string in t18
    move $a0, $s6
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print string (literal/global): str_18
    la $a0, str_18
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $v0, 10
    syscall