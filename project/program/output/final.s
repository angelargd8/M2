

# ===== Compiscript Program =====

.data
this: .word 0
g_rect: .word 0
exc_handler: .word 0
exc_value: .word 0
str_div_zero: .asciiz "division by zero"
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

Shape.setId:
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
    move $t0, $t0
    # setprop id
    sw $t0, 0($t1)
Shape.setId_epilog:
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
Shape.getId:
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
    # getprop id -> t2
    lw $t1, 0($t0)
    move $t1, $t1
    move $v0, $t1
Shape.getId_epilog:
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
    j Shape.getId_epilog
Rectangle.setDimensions:
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
    move $t0, $t0
    # setprop width
    sw $t0, 4($t1)
    lw $t0, 12($fp)
    la $t1, this
    lw $t1, 0($t1)
    move $t0, $t0
    # setprop height
    sw $t0, 8($t1)
Rectangle.setDimensions_epilog:
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
Rectangle.area:
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
    # getprop width -> t1
    lw $t1, 4($t0)
    la $t0, this
    lw $t0, 0($t0)
    # getprop height -> t3
    lw $t2, 8($t0)
    move $t1, $t1
    move $t2, $t2
    mul $t0, $t1, $t2
    move $t0, $t0
    move $v0, $t0
Rectangle.area_epilog:
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
    j Rectangle.area_epilog
Rectangle.describe:
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
    # getprop id -> t3
    lw $t1, 0($t0)
    move $t1, $t1
    move $a0, $t1
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t1, this
    lw $t1, 0($t1)
    move $t1, $t1
    addi $sp, $sp, -4
    sw $t1, 0($sp)
    move $t1, $t1
    la $t9, this
    sw $t1, 0($t9)
    jal Rectangle.area
    addi $sp, $sp, 4
    move $t1, $v0
    move $t1, $t1
    move $a0, $t1
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
Rectangle.describe_epilog:
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
    # newobj Rectangle -> t3
    li $a0, 12
    li $v0, 9
    syscall
    move $t0, $v0
    la $t9, g_rect
    sw $t0, 0($t9)
    li $t1, 500
    la $t2, g_rect
    lw $t2, 0($t2)
    move $t2, $t2
    addi $sp, $sp, -4
    sw $t2, 0($sp)
    move $t1, $t1
    addi $sp, $sp, -4
    sw $t1, 0($sp)
    move $t2, $t2
    la $t9, this
    sw $t2, 0($t9)
    jal Shape.setId
    addi $sp, $sp, 8
    move $t1, $v0
    li $t2, 10
    li $t3, 20
    la $t4, g_rect
    lw $t4, 0($t4)
    move $t4, $t4
    addi $sp, $sp, -4
    sw $t4, 0($sp)
    move $t2, $t2
    addi $sp, $sp, -4
    sw $t2, 0($sp)
    move $t3, $t3
    addi $sp, $sp, -4
    sw $t3, 0($sp)
    move $t4, $t4
    la $t9, this
    sw $t4, 0($t9)
    jal Rectangle.setDimensions
    addi $sp, $sp, 12
    move $t3, $v0
    la $t2, g_rect
    lw $t2, 0($t2)
    move $t2, $t2
    addi $sp, $sp, -4
    sw $t2, 0($sp)
    move $t2, $t2
    la $t9, this
    sw $t2, 0($t9)
    jal Shape.getId
    addi $sp, $sp, 4
    move $t2, $v0
    move $t2, $t2
    move $a0, $t2
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t2, g_rect
    lw $t2, 0($t2)
    move $t2, $t2
    addi $sp, $sp, -4
    sw $t2, 0($sp)
    move $t2, $t2
    la $t9, this
    sw $t2, 0($t9)
    jal Rectangle.area
    addi $sp, $sp, 4
    move $t2, $v0
    move $t2, $t2
    move $a0, $t2
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t2, g_rect
    lw $t2, 0($t2)
    move $t2, $t2
    addi $sp, $sp, -4
    sw $t2, 0($sp)
    move $t2, $t2
    la $t9, this
    sw $t2, 0($t9)
    jal Rectangle.describe
    addi $sp, $sp, 4
    move $t2, $v0
    li $v0, 10
    syscall