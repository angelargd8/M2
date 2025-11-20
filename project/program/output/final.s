

# ===== Compiscript Program =====

.data
PI: .word 314
greeting: .word str_3
flag: .word 0
numbers: .word 1, 2, 3, 4, 5
matrix_row_0: .word 1, 2
matrix_row_1: .word 3, 4
matrix: .word matrix_row_0, matrix_row_1
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
    # print string (literal/global): str_0
    la $a0, str_0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print int from temp t1 = 1
    li $a0, 1
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, str_1
    la $t1, str_2
    li $a0, 512
    li $v0, 9
    syscall
    move $t2, $v0
    move $t4, $t2
    move $t5, $t0
    move $t6, $t1
concat_copy_a_t3:
    lb $t0, 0($t5)
    sb $t0, 0($t4)
    beq $t0, $zero, concat_copy_b_t3
    addi $t5, $t5, 1
    addi $t4, $t4, 1
    j concat_copy_a_t3
concat_copy_b_t3:
    lb $t0, 0($t6)
    sb $t0, 0($t4)
    beq $t0, $zero, concat_done_t3
    addi $t6, $t6, 1
    addi $t4, $t4, 1
    j concat_copy_b_t3
concat_done_t3:
    # print dynamic string in t3
    move $a0, $t2
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t2, 314
    la $t9, PI
    sw $t2, 0($t9)
    la $t2, str_3
    la $t9, greeting
    sw $t2, 0($t9)
    # alloc_array size=5
    li $a0, 24
    li $v0, 9
    syscall
    move $t2, $v0
    li $t9, 5
    sw $t9, 0($t2)
    li $t8, 1
    # setidx t3[0] = t2
    sw $t8, 4($t2)
    li $t8, 2
    # setidx t3[1] = t2
    sw $t8, 8($t2)
    li $t8, 3
    # setidx t3[2] = t2
    sw $t8, 12($t2)
    li $t8, 4
    # setidx t3[3] = t2
    sw $t8, 16($t2)
    li $t8, 5
    # setidx t3[4] = t2
    sw $t8, 20($t2)
    la $t2, str_3
    la $t9, numbers
    sw $t2, 0($t9)
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
    li $t8, 1
    # setidx t2[0] = t1
    sw $t8, 4($t1)
    li $t8, 2
    # setidx t2[1] = t1
    sw $t8, 8($t1)
    li $t8, 5
    # setidx t3[0] = t2
    sw $t8, 4($t2)
    # alloc_array size=2
    li $a0, 12
    li $v0, 9
    syscall
    move $t1, $v0
    li $t9, 2
    sw $t9, 0($t1)
    li $t8, 3
    # setidx t2[0] = t1
    sw $t8, 4($t1)
    li $t8, 4
    # setidx t2[1] = t1
    sw $t8, 8($t1)
    li $t8, 5
    # setidx t3[1] = t2
    sw $t8, 8($t2)
    la $t2, str_3
    la $t9, matrix
    sw $t2, 0($t9)
    la $t0, PI
    lw $a0, 0($t0)
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, greeting
    lw $a0, 0($t0)
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, flag
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