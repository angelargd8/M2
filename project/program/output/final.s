

# ===== Compiscript Program =====

.data
g_i: .word 0
g_k: .word 0
g_nums: .word 1, 2, 3, 4
g_total: .word 0
g_day: .word 3
str_0: .asciiz "==WHILE=="
str_1: .asciiz "i = "
str_2: .asciiz "==FOR=="
str_3: .asciiz "j = "
str_4: .asciiz "==do-while=="
str_5: .asciiz "k = "
str_6: .asciiz "==foreach=="
str_7: .asciiz "Total = "
str_8: .asciiz "==break - continue =="
str_9: .asciiz "continue at p = 3"
str_10: .asciiz "break at p = 7"
str_11: .asciiz "p = "
str_12: .asciiz "==switch=="
str_13: .asciiz "Monday"
str_14: .asciiz "Tuesday"
str_15: .asciiz "Wednesday"
str_16: .asciiz "Unknown day"
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
    li $t0, 0
    move $t0, $t0
    la $t9, g_i
    sw $t0, 0($t9)
L1:
    la $t0, g_i
    lw $t0, 0($t0)
    li $t1, 5
    move $t0, $t0
    move $t1, $t1
    slt $t2, $t0, $t1
    move $t2, $t2
    beq $t2, $zero, L2
    la $t1, g_i
    lw $t1, 0($t1)
    move $t1, $t1
    move $a0, $t1
    jal cs_int_to_string
    move $t0, $v0
    la $t3, str_1
    move $t4, $t0
    li $a0, 512
    li $v0, 9
    syscall
    move $t5, $v0
    move $t6, $t5
concat_copy_a_t1_1:
    lb $t7, 0($t3)
    sb $t7, 0($t6)
    beq $t7, $zero, concat_copy_b_t1_1
    addi $t3, $t3, 1
    addi $t6, $t6, 1
    j concat_copy_a_t1_1
concat_copy_b_t1_1:
    lb $t7, 0($t4)
    sb $t7, 0($t6)
    beq $t7, $zero, concat_done_t1_1
    addi $t4, $t4, 1
    addi $t6, $t6, 1
    j concat_copy_b_t1_1
concat_done_t1_1:
    sb $zero, 0($t6)
    move $t0, $t5
    # print dynamic string in t1
    move $a0, $t0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, g_i
    lw $t0, 0($t0)
    li $t1, 1
    move $t0, $t0
    move $t1, $t1
    add $t2, $t0, $t1
    move $t2, $t2
    la $t9, g_i
    sw $t2, 0($t9)
    j L1
L2:
    # print string (literal/global): str_2
    la $a0, str_2
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t2, 0
    move $t1, $t2
L3:
    li $t2, 4
    move $t1, $t1
    move $t2, $t2
    slt $t0, $t1, $t2
    move $t0, $t0
    beq $t0, $zero, L4
    move $t1, $t1
    move $a0, $t1
    jal cs_int_to_string
    move $t2, $v0
    la $t8, str_3
    move $t9, $t2
    li $a0, 512
    li $v0, 9
    syscall
    move $s0, $v0
    move $s1, $s0
concat_copy_a_t3_2:
    lb $s2, 0($t8)
    sb $s2, 0($s1)
    beq $s2, $zero, concat_copy_b_t3_2
    addi $t8, $t8, 1
    addi $s1, $s1, 1
    j concat_copy_a_t3_2
concat_copy_b_t3_2:
    lb $s2, 0($t9)
    sb $s2, 0($s1)
    beq $s2, $zero, concat_done_t3_2
    addi $t9, $t9, 1
    addi $s1, $s1, 1
    j concat_copy_b_t3_2
concat_done_t3_2:
    sb $zero, 0($s1)
    move $t2, $s0
    # print dynamic string in t3
    move $a0, $t2
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L5:
    li $t2, 1
    move $t1, $t1
    move $t2, $t2
    add $t0, $t1, $t2
    move $t1, $t0
    j L3
L4:
    # print string (literal/global): str_4
    la $a0, str_4
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t0, 0
    move $t0, $t0
    la $t9, g_k
    sw $t0, 0($t9)
L6:
    la $t2, g_k
    lw $t2, 0($t2)
    move $t2, $t2
    move $a0, $t2
    jal cs_int_to_string
    move $s3, $v0
    la $s4, str_5
    move $s5, $s3
    li $a0, 512
    li $v0, 9
    syscall
    move $s6, $v0
    move $s7, $s6
concat_copy_a_t4_3:
    lb $t3, 0($s4)
    sb $t3, 0($s7)
    beq $t3, $zero, concat_copy_b_t4_3
    addi $s4, $s4, 1
    addi $s7, $s7, 1
    j concat_copy_a_t4_3
concat_copy_b_t4_3:
    lb $t3, 0($s5)
    sb $t3, 0($s7)
    beq $t3, $zero, concat_done_t4_3
    addi $s5, $s5, 1
    addi $s7, $s7, 1
    j concat_copy_b_t4_3
concat_done_t4_3:
    sb $zero, 0($s7)
    move $s3, $s6
    # print dynamic string in t4
    move $a0, $s3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $s3, g_k
    lw $s3, 0($s3)
    li $t2, 1
    move $s3, $s3
    move $t2, $t2
    add $t0, $s3, $t2
    move $t0, $t0
    la $t9, g_k
    sw $t0, 0($t9)
    la $t0, g_k
    lw $t0, 0($t0)
    li $t2, 3
    move $t0, $t0
    move $t2, $t2
    slt $s3, $t0, $t2
    move $s3, $s3
    bne $s3, $zero, L6
L7:
    # print string (literal/global): str_6
    la $a0, str_6
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # alloc_array size=4
    li $a0, 20
    li $v0, 9
    syscall
    move $s3, $v0
    li $t9, 4
    sw $t9, 0($s3)
    li $t2, 1
    move $t8, $t2
    # setidx t4[0] = t3
    sw $t8, 4($s3)
    li $t2, 2
    move $t8, $t2
    # setidx t4[1] = t3
    sw $t8, 8($s3)
    li $t2, 3
    move $t8, $t2
    # setidx t4[2] = t3
    sw $t8, 12($s3)
    li $t2, 4
    move $t8, $t2
    # setidx t4[3] = t3
    sw $t8, 16($s3)
    la $t9, g_nums
    sw $s3, 0($t9)
    li $s3, 0
    move $s3, $s3
    la $t9, g_total
    sw $s3, 0($t9)
    la $s3, g_nums
    lw $s3, 0($s3)
    li $t2, 0
    # array_length t4 -> t1
    lw $t0, 0($s3)
L8:
    move $t2, $t2
    move $t0, $t0
    slt $t4, $t2, $t0
    move $t4, $t4
    beq $t4, $zero, L9
    # getidx t4[t3] -> t6 (dinámico)
    sll $t8, $t2, 2
    addi $t8, $t8, 4
    add $t8, $s3, $t8
    lw $t5, 0($t8)
    move $t6, $t5
    la $t7, g_total
    lw $t7, 0($t7)
    move $t7, $t7
    move $t6, $t6
    add $t8, $t7, $t6
    move $t8, $t8
    la $t9, g_total
    sw $t8, 0($t9)
L10:
    li $t8, 1
    move $t2, $t2
    move $t8, $t8
    add $t7, $t2, $t8
    move $t2, $t7
    j L8
L9:
    la $t9, g_total
    lw $t9, 0($t9)
    move $t9, $t9
    move $a0, $t9
    jal cs_int_to_string
    move $s0, $v0
    la $s1, str_7
    move $s2, $s0
    li $a0, 512
    li $v0, 9
    syscall
    move $s4, $v0
    move $s5, $s4
concat_copy_a_t11_4:
    lb $s6, 0($s1)
    sb $s6, 0($s5)
    beq $s6, $zero, concat_copy_b_t11_4
    addi $s1, $s1, 1
    addi $s5, $s5, 1
    j concat_copy_a_t11_4
concat_copy_b_t11_4:
    lb $s6, 0($s2)
    sb $s6, 0($s5)
    beq $s6, $zero, concat_done_t11_4
    addi $s2, $s2, 1
    addi $s5, $s5, 1
    j concat_copy_b_t11_4
concat_done_t11_4:
    sb $zero, 0($s5)
    move $s0, $s4
    # print dynamic string in t11
    move $a0, $s0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print string (literal/global): str_8
    la $a0, str_8
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $s0, 0
    move $t9, $s0
L11:
    li $s0, 10
    move $t9, $t9
    move $s0, $s0
    slt $s3, $t9, $s0
    move $s3, $s3
    beq $s3, $zero, L12
    li $s3, 3
    move $t9, $t9
    move $s3, $s3
    xor $s0, $t9, $s3
    sltiu $s0, $s0, 1
    move $s0, $s0
    beq $s0, $zero, L14
    # print string (literal/global): str_9
    la $a0, str_9
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    j L13
L14:
    li $s0, 7
    move $t9, $t9
    move $s0, $s0
    xor $s3, $t9, $s0
    sltiu $s3, $s3, 1
    move $s3, $s3
    beq $s3, $zero, L16
    # print string (literal/global): str_10
    la $a0, str_10
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    j L12
L16:
    move $t9, $t9
    move $a0, $t9
    jal cs_int_to_string
    move $s0, $v0
    la $s7, str_11
    move $t3, $s0
    li $a0, 512
    li $v0, 9
    syscall
    move $s1, $v0
    move $s2, $s1
concat_copy_a_t11_5:
    lb $s4, 0($s7)
    sb $s4, 0($s2)
    beq $s4, $zero, concat_copy_b_t11_5
    addi $s7, $s7, 1
    addi $s2, $s2, 1
    j concat_copy_a_t11_5
concat_copy_b_t11_5:
    lb $s4, 0($t3)
    sb $s4, 0($s2)
    beq $s4, $zero, concat_done_t11_5
    addi $t3, $t3, 1
    addi $s2, $s2, 1
    j concat_copy_b_t11_5
concat_done_t11_5:
    sb $zero, 0($s2)
    move $s0, $s1
    # print dynamic string in t11
    move $a0, $s0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L13:
    li $s0, 1
    move $t9, $t9
    move $s0, $s0
    add $s3, $t9, $s0
    move $t9, $s3
    j L11
L12:
    # print string (literal/global): str_12
    la $a0, str_12
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $s3, 3
    move $s3, $s3
    la $t9, g_day
    sw $s3, 0($t9)
    la $s3, g_day
    lw $s3, 0($s3)
    li $s0, 1
    move $s3, $s3
    move $s0, $s0
    xor $s5, $s3, $s0
    sltiu $s5, $s5, 1
    move $s5, $s5
    bne $s5, $zero, L19
    move $s3, $s3
    li $s6, 2
    xor $s7, $s3, $s6
    sltiu $s7, $s7, 1
    move $s7, $s7
    bne $s7, $zero, L20
    move $s3, $s3
    li $t3, 3
    xor $s1, $s3, $t3
    sltiu $s1, $s1, 1
    move $s1, $s1
    bne $s1, $zero, L21
    j L22
L19:
    # print string (literal/global): str_13
    la $a0, str_13
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L20:
    # print string (literal/global): str_14
    la $a0, str_14
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L21:
    # print string (literal/global): str_15
    la $a0, str_15
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L22:
    # print string (literal/global): str_16
    la $a0, str_16
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
L18:
    li $v0, 10
    syscall