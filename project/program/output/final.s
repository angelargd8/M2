

# ===== Compiscript Program =====

.data
this: .word 0
g_addFive: .word 0
g_restar: .word 0
g_multiplicar: .word 0
g_dividir: .word 0
exc_handler: .word 0
exc_value: .word 0
str_div_zero: .asciiz "division by zero"
str_0: .asciiz "==SUMA=="
str_1: .asciiz "5 + 2 = "
str_2: .asciiz "==RESTA=="
str_3: .asciiz "5 - 2 = "
str_4: .asciiz "==MULTIPLICACION=="
str_5: .asciiz "5 * 2 = "
str_6: .asciiz "==DIVISION=="
str_7: .asciiz "10 / 2 = "
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

makeAdder:
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
    li $t1, 2
    move $t0, $t0
    move $t1, $t1
    add $t2, $t0, $t1
    move $t2, $t2
    move $v0, $t2
makeAdder_epilog:
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
    j makeAdder_epilog
RESTA:
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
    li $t1, 2
    move $t0, $t0
    move $t1, $t1
    sub $t2, $t0, $t1
    move $t2, $t2
    move $v0, $t2
RESTA_epilog:
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
    j RESTA_epilog
MULTIPLICACION:
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
    li $t1, 2
    move $t0, $t0
    move $t1, $t1
    mul $t2, $t0, $t1
    move $t2, $t2
    move $v0, $t2
MULTIPLICACION_epilog:
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
    j MULTIPLICACION_epilog
DIVISION:
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
    li $t1, 2
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
    move $v0, $t2
DIVISION_epilog:
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
    j DIVISION_epilog
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
    # print string (literal/global): str_0
    la $a0, str_0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t0, 5
    move $t0, $t0
    addi $sp, $sp, -4
    sw $t0, 0($sp)
    jal makeAdder
    addi $sp, $sp, 4
    move $t0, $v0
    move $t0, $t0
    la $t9, g_addFive
    sw $t0, 0($t9)
    # print string (literal/global): str_1
    la $a0, str_1
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, g_addFive
    lw $a0, 0($t0)
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print string (literal/global): str_2
    la $a0, str_2
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t0, 5
    move $t0, $t0
    addi $sp, $sp, -4
    sw $t0, 0($sp)
    jal RESTA
    addi $sp, $sp, 4
    move $t0, $v0
    move $t0, $t0
    la $t9, g_restar
    sw $t0, 0($t9)
    # print string (literal/global): str_3
    la $a0, str_3
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, g_restar
    lw $a0, 0($t0)
    li $v0, 1
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
    li $t0, 5
    move $t0, $t0
    addi $sp, $sp, -4
    sw $t0, 0($sp)
    jal MULTIPLICACION
    addi $sp, $sp, 4
    move $t0, $v0
    move $t0, $t0
    la $t9, g_multiplicar
    sw $t0, 0($t9)
    # print string (literal/global): str_5
    la $a0, str_5
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, g_multiplicar
    lw $a0, 0($t0)
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    # print string (literal/global): str_6
    la $a0, str_6
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $t0, 10
    move $t0, $t0
    addi $sp, $sp, -4
    sw $t0, 0($sp)
    jal DIVISION
    addi $sp, $sp, 4
    move $t0, $v0
    move $t0, $t0
    la $t9, g_dividir
    sw $t0, 0($t9)
    # print string (literal/global): str_7
    la $a0, str_7
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, g_dividir
    lw $a0, 0($t0)
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $v0, 10
    syscall