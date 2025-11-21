

# ===== Compiscript Program =====

.data
this: .word 0
g_multiples: .word 0
exc_handler: .word 0
exc_value: .word 0
str_div_zero: .asciiz "division by zero"
str_0: .asciiz "Multiples of 2: "
str_1: .asciiz " "
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
    move $t8, $t3
    # setidx t1[0] = t4
    sw $t8, 4($t0)
    lw $t3, 8($fp)
    li $t2, 2
    move $t3, $t3
    move $t2, $t2
    mul $t1, $t3, $t2
    move $t8, $t1
    # setidx t1[1] = t2
    sw $t8, 8($t0)
    lw $t1, 8($fp)
    li $t2, 3
    move $t1, $t1
    move $t2, $t2
    mul $t3, $t1, $t2
    move $t8, $t3
    # setidx t1[2] = t4
    sw $t8, 12($t0)
    lw $t3, 8($fp)
    li $t2, 4
    move $t3, $t3
    move $t2, $t2
    mul $t1, $t3, $t2
    move $t8, $t1
    # setidx t1[3] = t2
    sw $t8, 16($t0)
    lw $t1, 8($fp)
    li $t2, 5
    move $t1, $t1
    move $t2, $t2
    mul $t3, $t1, $t2
    move $t8, $t3
    # setidx t1[4] = t4
    sw $t8, 20($t0)
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
    li $t0, 2
    move $t0, $t0
    addi $sp, $sp, -4
    sw $t0, 0($sp)
    jal getMultiples
    addi $sp, $sp, 4
    move $t0, $v0
    la $t9, g_multiples
    sw $t0, 0($t9)
    la $t1, g_multiples
    lw $t1, 0($t1)
    li $t2, 0
    # getidx t4[t3] -> t2 (dinámico)
    sll $t6, $t2, 2
    addi $t6, $t6, 4
    lw $t8, 0($t1)
    move $t7, $t2
    bge $t7, $t8, getidx_oob_dyn_t2
    add $t6, $t1, $t6
    lw $t3, 0($t6)
    j getidx_done_t2
getidx_oob_static_t2:
    li $t3, 0
    j getidx_done_t2
getidx_oob_dyn_t2:
    li $t3, 0
getidx_done_t2:
    move $t3, $t3
    addi $sp, $sp, -4
    sw $a0, 0($sp)
    move $a0, $t3
    jal cs_int_to_string
    lw $a0, 0($sp)
    addi $sp, $sp, 4
    move $t2, $v0
    la $t4, str_0
    move $t5, $t2
    li $a0, 512
    li $v0, 9
    syscall
    move $t6, $v0
    move $t7, $t6
concat_copy_a_t3_1:
    lb $t8, 0($t4)
    sb $t8, 0($t7)
    beq $t8, $zero, concat_copy_b_t3_1
    addi $t4, $t4, 1
    addi $t7, $t7, 1
    j concat_copy_a_t3_1
concat_copy_b_t3_1:
    lb $t8, 0($t5)
    sb $t8, 0($t7)
    beq $t8, $zero, concat_done_t3_1
    addi $t5, $t5, 1
    addi $t7, $t7, 1
    j concat_copy_b_t3_1
concat_done_t3_1:
    sb $zero, 0($t7)
    move $t2, $t6
    move $t9, $t2
    la $s0, str_1
    li $a0, 512
    li $v0, 9
    syscall
    move $s1, $v0
    move $s2, $s1
concat_copy_a_t1_2:
    lb $s3, 0($t9)
    sb $s3, 0($s2)
    beq $s3, $zero, concat_copy_b_t1_2
    addi $t9, $t9, 1
    addi $s2, $s2, 1
    j concat_copy_a_t1_2
concat_copy_b_t1_2:
    lb $s3, 0($s0)
    sb $s3, 0($s2)
    beq $s3, $zero, concat_done_t1_2
    addi $s0, $s0, 1
    addi $s2, $s2, 1
    j concat_copy_b_t1_2
concat_done_t1_2:
    sb $zero, 0($s2)
    move $s4, $s1
    # print dynamic string in t1
    move $a0, $s4
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $s4, g_multiples
    lw $s4, 0($s4)
    li $t3, 1
    # getidx t1[t2] -> t3 (dinámico)
    sll $t6, $t3, 2
    addi $t6, $t6, 4
    lw $t8, 0($s4)
    move $t7, $t3
    bge $t7, $t8, getidx_oob_dyn_t3
    add $t6, $s4, $t6
    lw $t2, 0($t6)
    j getidx_done_t3
getidx_oob_static_t3:
    li $t2, 0
    j getidx_done_t3
getidx_oob_dyn_t3:
    li $t2, 0
getidx_done_t3:
    move $t2, $t2
    move $a0, $t2
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $v0, 10
    syscall