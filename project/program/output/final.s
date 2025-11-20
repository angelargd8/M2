

# ===== Compiscript Program =====

.data
addFive: .word 0
str_0: .asciiz "5 + 1 = "
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

makeAdder:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    lw $t0, 8($fp)
    move $t0, $t0
    li $t1, 1
    add $t2, $t0, $t1
    move $t2, $t2
    move $v0, $t2
    # ---- EPILOG ----
    move $sp, $fp
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    jr $ra
    # ---- EPILOG ----
    move $sp, $fp
    lw $ra, 0($sp)
    lw $fp, 4($sp)
    addi $sp, $sp, 8
    jr $ra
main:
    addi $sp, $sp, -8
    sw $fp, 4($sp)
    sw $ra, 0($sp)
    move $fp, $sp
    li $t2, 5
    addi $sp, $sp, -4
    sw $t2, 0($sp)
    jal makeAdder
    addi $sp, $sp, 4
    move $t2, $v0
    move $t2, $t2
    la $t9, addFive
    sw $t2, 0($t9)
    # print string (literal/global): str_0
    la $a0, str_0
    li $v0, 4
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    la $t0, addFive
    lw $a0, 0($t0)
    li $v0, 1
    syscall
    la $a0, nl
    li $v0, 4
    syscall
    li $v0, 10
    syscall