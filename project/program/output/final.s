

# ===== Compiscript Program =====

.data
this: .word 0
g_dog: .word 0
str_0: .asciiz " makes a sound."
str_1: .asciiz " barks."
str_2: .asciiz "Rex"
nl: .asciiz "\n"
str_lbr: .asciiz "["
str_rbr: .asciiz "]"
str_comma: .asciiz ", "
str_array: .asciiz "[array]"

.text
.globl main
.globl cs_int_to_string

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

Animal.constructor:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    lw $t0, 8($fp)
    la $t1, this
    lw $t1, 0($t1)
    move $t1, $t1
    move $t0, $t0
    # setprop name
    sw $t0, 0($t1)
    # ---- EPILOG ----
    move $sp, $fp
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    jr $ra
Animal.speak:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
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
concat_copy_a_t3_1:
    lb $t6, 0($t2)
    sb $t6, 0($t5)
    beq $t6, $zero, concat_copy_b_t3_1
    addi $t2, $t2, 1
    addi $t5, $t5, 1
    j concat_copy_a_t3_1
concat_copy_b_t3_1:
    lb $t6, 0($t3)
    sb $t6, 0($t5)
    beq $t6, $zero, concat_done_t3_1
    addi $t3, $t3, 1
    addi $t5, $t5, 1
    j concat_copy_b_t3_1
concat_done_t3_1:
    sb $zero, 0($t5)
    move $t7, $t4
    move $t7, $t7
    move $v0, $t7
    # ---- EPILOG ----
    move $sp, $fp
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    jr $ra
    # ---- EPILOG ----
    move $sp, $fp
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    jr $ra
Dog.speak:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    la $t0, this
    lw $t0, 0($t0)
    move $t0, $t0
    # getprop name -> t1
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
    # ---- EPILOG ----
    move $sp, $fp
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    jr $ra
    # ---- EPILOG ----
    move $sp, $fp
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    jr $ra
main:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    # newobj Dog -> t3
    li $a0, 8
    li $v0, 9
    syscall
    move $t0, $v0
    la $t1, str_2
    # setprop name
    sw $t1, 0($t0)
    la $t9, g_dog
    sw $t0, 0($t9)
    la $t2, g_dog
    lw $t2, 0($t2)
    move $t2, $t2
    addi $sp, $sp, -4
    sw $t2, 0($sp)
    move $t2, $t2
    la $t9, this
    sw $t2, 0($t9)
    jal Dog.speak
    move $t2, $v0
    # print dynamic string in t3
    move $a0, $t2
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $v0, 10
    syscall