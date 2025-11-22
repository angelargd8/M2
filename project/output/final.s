

# ===== Compiscript Program =====

.data
this: .word 0
exc_handler: .word 0
exc_value: .word 0
str_div_zero: .asciiz "division by zero"
str_0: .asciiz "Trying risky operation"
str_1: .asciiz "Caught exception: "
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

risky:
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
    # push_handler L1
    la $t9, exc_handler
    la $t8, L1
    sw $t8, 0($t9)
    # print string (literal/global): str_0
    la $a0, str_0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t0, 10
    li $t1, 0
    move $t0, $t0
    move $t1, $t1
    beq $t1, $zero, DZ_ERR_L1
    div $t0, $t1
    mflo $t2
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
    move $t2, $t2
    sw $t2, -4($fp)
    # pop_handler
    la $t9, exc_handler
    sw $zero, 0($t9)
    la $t9, exc_value
    sw $zero, 0($t9)
    j L2
L1:
    # get_exception
    la $t9, exc_value
    lw $t2, 0($t9)
    la $t8, exc_tmp
    sw $t2, 0($t8)
    move $t2, $t2
    # fallback store to exc_tmp (addr e)
    la $t9, exc_tmp
    sw $t2, 0($t9)
    la $t9, exc_tmp
    lw $t0, 0($t9)
    la $t3, str_1
    move $t4, $t0
    li $a0, 512
    li $v0, 9
    syscall
    move $t5, $v0
    move $t6, $t5
concat_copy_a_t4_1:
    lb $t7, 0($t3)
    sb $t7, 0($t6)
    beq $t7, $zero, concat_copy_b_t4_1
    addi $t3, $t3, 1
    addi $t6, $t6, 1
    j concat_copy_a_t4_1
concat_copy_b_t4_1:
    lb $t7, 0($t4)
    sb $t7, 0($t6)
    beq $t7, $zero, concat_done_t4_1
    addi $t4, $t4, 1
    addi $t6, $t6, 1
    j concat_copy_b_t4_1
concat_done_t4_1:
    sb $zero, 0($t6)
    move $t8, $t5
    # print dynamic string in t4
    move $a0, $t8
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L2:
risky_epilog:
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
    jal risky
    move $t0, $v0
    li $v0, 10
    syscall