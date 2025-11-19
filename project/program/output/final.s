

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
main:
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

    # ===== CONCAT START =====
    la $t0, str_1
    move $t1, $zero
concat_left_len_loop:
    lb $t2, 0($t0)
    beq $t2, $zero, concat_left_len_done
    addi $t1, $t1, 1
    addi $t0, $t0, 1
    j concat_left_len_loop
concat_left_len_done:
    la $t0, str_2
    move $t3, $zero
concat_right_len_loop:
    lb $t2, 0($t0)
    beq $t2, $zero, concat_right_len_done
    addi $t3, $t3, 1
    addi $t0, $t0, 1
    j concat_right_len_loop
concat_right_len_done:
    add $t4, $t1, $t3
    addi $t4, $t4, 1
    move $a0, $t4
    li $v0, 9         # syscall sbrk
    syscall
    move $t5, $v0     # t5 = new buffer
    la $t0, str_1
    move $t6, $t5
concat_copy_left:
    lb $t2, 0($t0)
    beq $t2, $zero, concat_left_done_copy
    sb $t2, 0($t6)
    addi $t6, $t6, 1
    addi $t0, $t0, 1
    j concat_copy_left
concat_left_done_copy:
    la $t0, str_2
concat_copy_right:
    lb $t2, 0($t0)
    beq $t2, $zero, concat_right_done_copy
    sb $t2, 0($t6)
    addi $t6, $t6, 1
    addi $t0, $t0, 1
    j concat_copy_right
concat_right_done_copy:
    sb $zero, 0($t6)
    # ===== CONCAT END =====

    # print dynamic string in t3
    move $a0, $t5
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # alloc_array size=5
    li $a0, 24
    li $v0, 9
    syscall
    move $t0, $v0
    li $t9, 5
    sw $t9, 0($t0)
    li $t8, 1
    # setidx t3[0] = t2
    sw $t8, 4($t0)
    li $t8, 2
    # setidx t3[1] = t2
    sw $t8, 8($t0)
    li $t8, 3
    # setidx t3[2] = t2
    sw $t8, 12($t0)
    li $t8, 4
    # setidx t3[3] = t2
    sw $t8, 16($t0)
    li $t8, 5
    # setidx t3[4] = t2
    sw $t8, 20($t0)
    # alloc_array size=2
    li $a0, 12
    li $v0, 9
    syscall
    move $t0, $v0
    li $t9, 2
    sw $t9, 0($t0)
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
    sw $t8, 4($t0)
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
    sw $t8, 8($t0)
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