

# ===== Compiscript Program =====

.data
g_a: .word 5
g_b: .word 10
g_c: .word 10
str_0: .asciiz "B is greater than A"
str_1: .asciiz "A is greater than B"
str_2: .asciiz "A is greater than or equal to B"
str_3: .asciiz "A is less than or equal to B"
str_4: .asciiz "C is greater than or equal to B"
str_5: .asciiz "C is less than or equal to B"
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
    addi $sp, $sp, -12
    sw $ra, 8($sp)
    sw $s0, 4($sp)
    sw $s1, 0($sp)
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
    addi $t1, $t1, 1
    move $v0, $t1
cs_its_done:
    lw $s1, 0($sp)
    lw $s0, 4($sp)
    lw $ra, 8($sp)
    addi $sp, $sp, 12
    jr $ra

main:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    li $t0, 5
    la $t9, g_a
    sw $t0, 0($t9)
    li $t0, 10
    la $t9, g_b
    sw $t0, 0($t9)
    li $t0, 10
    la $t9, g_c
    sw $t0, 0($t9)
    la $t0, g_a
    lw $t0, 0($t0)
    la $t1, g_b
    lw $t1, 0($t1)
    move $t0, $t0
    move $t1, $t1
    slt $t2, $t0, $t1
    move $t2, $t2
    beq $t2, $zero, L1
    # print string (literal/global): str_0
    la $a0, str_0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L1:
    la $t2, g_a
    lw $t2, 0($t2)
    la $t1, g_b
    lw $t1, 0($t1)
    move $t2, $t2
    move $t1, $t1
    sgt $t0, $t2, $t1
    move $t0, $t0
    beq $t0, $zero, L3
    # print string (literal/global): str_1
    la $a0, str_1
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L3:
    la $t0, g_a
    lw $t0, 0($t0)
    la $t1, g_b
    lw $t1, 0($t1)
    move $t0, $t0
    move $t1, $t1
    sge $t2, $t0, $t1
    move $t2, $t2
    beq $t2, $zero, L5
    # print string (literal/global): str_2
    la $a0, str_2
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L5:
    la $t2, g_a
    lw $t2, 0($t2)
    la $t1, g_b
    lw $t1, 0($t1)
    move $t2, $t2
    move $t1, $t1
    sle $t0, $t2, $t1
    move $t0, $t0
    beq $t0, $zero, L7
    # print string (literal/global): str_3
    la $a0, str_3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L7:
    la $t0, g_c
    lw $t0, 0($t0)
    la $t1, g_b
    lw $t1, 0($t1)
    move $t0, $t0
    move $t1, $t1
    sge $t2, $t0, $t1
    move $t2, $t2
    beq $t2, $zero, L9
    # print string (literal/global): str_4
    la $a0, str_4
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L9:
    la $t2, g_c
    lw $t2, 0($t2)
    la $t1, g_b
    lw $t1, 0($t1)
    move $t2, $t2
    move $t1, $t1
    sle $t0, $t2, $t1
    move $t0, $t0
    beq $t0, $zero, L11
    # print string (literal/global): str_5
    la $a0, str_5
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L11:
    li $v0, 10
    syscall