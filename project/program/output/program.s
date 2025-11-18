.data
LSTR1: .asciiz "name"
LSTR2: .asciiz "name"
LSTR3: .asciiz " makes a sound."
LSTR4: .asciiz "name"
LSTR5: .asciiz " barks."
LSTR6: .asciiz "Hello, Compiscript!"
LSTR7: .asciiz "5 + 1 = "
LSTR8: .asciiz "Greater than 5"
LSTR9: .asciiz "5 or less"
LSTR10: .asciiz "Result is now "
LSTR11: .asciiz "Loop index: "
LSTR12: .asciiz "Number: "
LSTR13: .asciiz "It's seven"
LSTR14: .asciiz "It's six"
LSTR15: .asciiz "Something else"
LSTR16: .asciiz "Risky access: "
LSTR17: .asciiz "Caught an error: "
LSTR18: .asciiz "Rex"
LSTR19: .asciiz "First number: "
LSTR20: .asciiz "Multiples of 2: "
LSTR21: .asciiz ", "
LSTR22: .asciiz "Program finished."

# include runtime (ya está cargado por separado)

.text
.globl main

makeAdder:
lw $t1, 64($fp)
li $t2, 1
move $t0, $t1
move $t1, $t2
addu $t3, $t0, $t1
move $v0, $t3
jr $ra
jr $ra
Animal.constructor:
lw $t3, 64($fp)
la $t2, this
move $a0, $t2
la $a1, LSTR1
move $a2, $t3
jal cs_setprop
jr $ra
Animal.speak:
la $t3, this
move $a0, $t3
la $a1, LSTR2
jal cs_getprop
move $t2, $v0
la $t3, LSTR3
move $t0, $t2
move $t1, $t3
addu $t1, $t0, $t1
move $v0, $t1
jr $ra
jr $ra
Dog.speak:
la $t1, this
move $a0, $t1
la $a1, LSTR4
jal cs_getprop
move $t3, $v0
la $t1, LSTR5
move $t0, $t3
move $t1, $t1
addu $t2, $t0, $t1
move $v0, $t2
jr $ra
jr $ra
getMultiples:
li $a0, 5
jal cs_array_new
move $t2, $v0
lw $t1, 64($fp)
li $t3, 1
move $t0, $t1
move $t1, $t3
mul $t4, $t0, $t1
move $a0, $t2
li $a1, 0
move $a2, $t4
jal cs_array_set
lw $t4, 64($fp)
li $t3, 2
move $t0, $t4
move $t1, $t3
mul $t1, $t0, $t1
move $a0, $t2
li $a1, 1
move $a2, $t1
jal cs_array_set
lw $t1, 64($fp)
li $t3, 3
move $t0, $t1
move $t1, $t3
mul $t4, $t0, $t1
move $a0, $t2
li $a1, 2
move $a2, $t4
jal cs_array_set
lw $t4, 64($fp)
li $t3, 4
move $t0, $t4
move $t1, $t3
mul $t1, $t0, $t1
move $a0, $t2
li $a1, 3
move $a2, $t1
jal cs_array_set
lw $t1, 64($fp)
li $t3, 5
move $t0, $t1
move $t1, $t3
mul $t4, $t0, $t1
move $a0, $t2
li $a1, 4
move $a2, $t4
jal cs_array_set
sw $t2, 0($fp)
lw $t2, 0($fp)
move $v0, $t2
jr $ra
jr $ra
factorial:
lw $t2, 64($fp)
li $t4, 1
move $t0, $t4
move $t1, $t2
slt $t3, $t0, $t1
xori $t3, $t3, 1
move $t0, $t3
beq $t0, $zero, L1
li $t3, 1
move $v0, $t3
jr $ra
L1:
lw $t3, 64($fp)
lw $t4, 64($fp)
li $t2, 1
move $t0, $t4
move $t1, $t2
subu $t1, $t0, $t1
move $t0, $t1
addi $sp, $sp, -4
sw $t0, 0($sp)
jal factorial
move $t1, $v0
addi $sp, $sp, 4
move $t0, $t3
move $t1, $t1
mul $t2, $t0, $t1
move $v0, $t2
jr $ra
jr $ra
main:
move $fp, $sp
li $t2, 314
sw $t2, 0($fp)
la $t2, LSTR6
sw $t2, 16($fp)
li $a0, 5
jal cs_array_new
move $t2, $v0
li $t1, 1
move $a0, $t2
li $a1, 0
move $a2, $t1
jal cs_array_set
li $t1, 2
move $a0, $t2
li $a1, 1
move $a2, $t1
jal cs_array_set
li $t1, 3
move $a0, $t2
li $a1, 2
move $a2, $t1
jal cs_array_set
li $t1, 4
move $a0, $t2
li $a1, 3
move $a2, $t1
jal cs_array_set
li $t1, 5
move $a0, $t2
li $a1, 4
move $a2, $t1
jal cs_array_set
sw $t2, 52($fp)
li $a0, 2
jal cs_array_new
move $t2, $v0
li $a0, 2
jal cs_array_new
move $t1, $v0
li $t3, 1
move $a0, $t1
li $a1, 0
move $a2, $t3
jal cs_array_set
li $t3, 2
move $a0, $t1
li $a1, 1
move $a2, $t3
jal cs_array_set
move $a0, $t2
li $a1, 0
move $a2, $t1
jal cs_array_set
li $a0, 2
jal cs_array_new
move $t1, $v0
li $t3, 3
move $a0, $t1
li $a1, 0
move $a2, $t3
jal cs_array_set
li $t3, 4
move $a0, $t1
li $a1, 1
move $a2, $t3
jal cs_array_set
move $a0, $t2
li $a1, 1
move $a2, $t1
jal cs_array_set
sw $t2, 116($fp)
li $t2, 5
move $t0, $t2
addi $sp, $sp, -4
sw $t0, 0($sp)
jal makeAdder
move $t2, $v0
addi $sp, $sp, 4
sw $t2, 180($fp)
la $t2, LSTR7
lw $t1, 180($fp)
move $t0, $t2
move $t1, $t1
addu $t3, $t0, $t1
move $a0, $t3
jal cs_print
lw $t3, 180($fp)
li $t1, 5
move $t0, $t1
move $t1, $t3
slt $t2, $t0, $t1
move $t0, $t2
beq $t0, $zero, L3
la $t2, LSTR8
move $a0, $t2
jal cs_print
j L4
L3:
la $t2, LSTR9
move $a0, $t2
jal cs_print
L4:
L5:
lw $t2, 180($fp)
li $t1, 10
move $t0, $t2
move $t1, $t1
slt $t3, $t0, $t1
move $t0, $t3
beq $t0, $zero, L6
lw $t3, 180($fp)
li $t1, 1
move $t0, $t3
move $t1, $t1
addu $t2, $t0, $t1
sw $t2, 180($fp)
j L5
L6:
L7:
la $t2, LSTR10
lw $t1, 180($fp)
move $t0, $t2
move $t1, $t1
addu $t3, $t0, $t1
move $a0, $t3
jal cs_print
lw $t3, 180($fp)
li $t1, 1
move $t0, $t3
move $t1, $t1
subu $t2, $t0, $t1
sw $t2, 180($fp)
lw $t2, 180($fp)
li $t1, 7
move $t0, $t1
move $t1, $t2
slt $t3, $t0, $t1
move $t0, $t3
bne $t0, $zero, L7
L8:
li $t3, 0
la $t9, i
sw $t3, 0($t9)
L9:
la $t3, i
li $t1, 3
move $t0, $t3
move $t1, $t1
slt $t2, $t0, $t1
move $t0, $t2
beq $t0, $zero, L10
la $t2, LSTR11
la $t1, i
move $t0, $t2
move $t1, $t1
addu $t3, $t0, $t1
move $a0, $t3
jal cs_print
L11:
la $t3, i
li $t1, 1
move $t0, $t3
move $t1, $t1
addu $t2, $t0, $t1
la $t9, i
sw $t2, 0($t9)
j L9
L10:
lw $t2, 52($fp)
li $t1, 0
move $a0, $t2
jal cs_array_len
move $t3, $v0
L12:
move $t0, $t1
move $t1, $t3
slt $t4, $t0, $t1
move $t0, $t4
beq $t0, $zero, L13
move $a0, $t2
move $a1, $t1
jal cs_array_get
move $t5, $v0
la $t9, n
sw $t5, 0($t9)
la $t6, n
li $t7, 3
move $t0, $t6
move $t1, $t7
xor $t8, $t0, $t1
sltiu $t8, $t8, 1
move $t0, $t8
beq $t0, $zero, L15
j L14
L15:
la $t8, LSTR12
la $t7, n
move $t0, $t8
move $t1, $t7
addu $t6, $t0, $t1
move $a0, $t6
jal cs_print
la $t6, n
li $t7, 4
move $t0, $t7
move $t1, $t6
slt $t8, $t0, $t1
move $t0, $t8
beq $t0, $zero, L17
j L13
L17:
L14:
li $t8, 1
move $t0, $t1
move $t1, $t8
addu $t7, $t0, $t1
move $t1, $t7
j L12
L13:
lw $t2, 180($fp)
li $t6, 7
move $t0, $t2
move $t1, $t6
xor $t9, $t0, $t1
sltiu $t9, $t9, 1
move $t0, $t9
bne $t0, $zero, L20
li $t0, 6
move $t0, $t2
move $t1, $t0
xor $t1, $t0, $t1
sltiu $t1, $t1, 1
move $t0, $t1
bne $t0, $zero, L21
j L22
L20:
la $t2, LSTR13
move $a0, $t2
jal cs_print
L21:
la $t2, LSTR14
move $a0, $t2
jal cs_print
L22:
la $t2, LSTR15
move $a0, $t2
jal cs_print
L19:
la $a0, L23
jal cs_push_handler
lw $t2, 52($fp)
li $t2, 10
move $a0, $t2
move $a1, $t2
jal cs_array_get
move $t3, $v0
la $t9, risky
sw $t3, 0($t9)
la $t3, LSTR16
la $t2, risky
move $t0, $t3
move $t1, $t2
addu $t2, $t0, $t1
move $a0, $t2
jal cs_print
jal cs_pop_handler
j L24
L23:
jal cs_get_exception
move $t2, $v0
la $t9, err
sw $t2, 0($t9)
la $t2, LSTR17
la $t3, err
move $t0, $t2
move $t1, $t3
addu $t4, $t0, $t1
move $a0, $t4
jal cs_print
L24:
la $t4, LSTR18
li $a0, 8
jal cs_alloc_object
move $t3, $v0
la $t0, _init_Dog
move $a0, $t3
jalr $t0
sw $t3, 196($fp)
lw $t3, 196($fp)
jal speak
move $t3, $v0
move $a0, $t3
jal cs_print
lw $t3, 52($fp)
li $t4, 0
move $a0, $t3
move $a1, $t4
jal cs_array_get
move $t2, $v0
sw $t2, 228($fp)
la $t2, LSTR19
lw $t4, 228($fp)
move $t0, $t2
move $t1, $t4
addu $t3, $t0, $t1
move $a0, $t3
jal cs_print
li $t3, 2
move $t0, $t3
addi $sp, $sp, -4
sw $t0, 0($sp)
jal getMultiples
move $t3, $v0
addi $sp, $sp, 4
sw $t3, 244($fp)
la $t3, LSTR20
lw $t4, 244($fp)
li $t2, 0
move $a0, $t4
move $a1, $t2
jal cs_array_get
move $t5, $v0
move $t0, $t3
move $t1, $t5
addu $t2, $t0, $t1
la $t5, LSTR21
move $t0, $t2
move $t1, $t5
addu $t3, $t0, $t1
lw $t5, 244($fp)
li $t2, 1
move $a0, $t5
move $a1, $t2
jal cs_array_get
move $t4, $v0
move $t0, $t3
move $t1, $t4
addu $t2, $t0, $t1
move $a0, $t2
jal cs_print
la $t2, LSTR22
move $a0, $t2
jal cs_print
li $v0, 0
jr $ra