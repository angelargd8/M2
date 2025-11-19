

# ===== Compiscript Program =====

.data
str_0: .asciiz "Hello world"
str_1: .asciiz "Hello"
str_2: .asciiz "Compiscript"
nl: .asciiz "\n"

.text
.globl main
main:
    # print string: str_0
    la $a0, str_0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print int literal: 1
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
    li $v0, 9      # sbrk syscall
    syscall
    move $t5, $v0  # t5 = new buffer
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
    move $v1, $t5     # result pointer for t_dest=t3
    # ===== CONCAT END =====

    # print dynamic string in t3
    move $a0, $v1
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $v0, 10
    syscall