

# ===== Compiscript Program =====

.data
this: .word 0
exc_handler: .word 0
exc_value: .word 0
str_div_zero: .asciiz "division by zero"
str_0: .asciiz "==TRY-CATCH simple=="
str_1: .asciiz "NO DEBERÍA VERSE"
str_2: .asciiz "Caught an error:"
str_3: .asciiz "end"
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

main:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    # print string (literal/global): str_0
    la $a0, str_0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # push_handler L1
    la $t9, exc_handler
    la $t8, L1
    sw $t8, 0($t9)
    li $t0, 10
    move $t1, $t0
    li $t0, 0
    move $t2, $t0
    move $t1, $t1
    move $t2, $t2
    beq $t2, $zero, DZ_ERR_L1
    div $t1, $t2
    mflo $t0
    j DZ_OK_L1
DZ_ERR_L1:
    la $t8, str_div_zero
    la $t9, exc_value
    sw $t8, 0($t9)
    la $t9, exc_handler
    lw $t9, 0($t9)
    beq $t9, $zero, DZ_JMP_L1
    jr $t9
DZ_JMP_L1:
    li $v0, 10
    syscall
DZ_OK_L1:
    move $t3, $t0
    # print string (literal/global): str_1
    la $a0, str_1
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
    j L2
L1:
    # get_exception
    la $t9, exc_value
    lw $t0, 0($t9)
    # print string (literal/global): str_2
    la $a0, str_2
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print dynamic string in t5
    move $a0, $t0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L2:
    # print string (literal/global): str_3
    la $a0, str_3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $v0, 10
    syscall