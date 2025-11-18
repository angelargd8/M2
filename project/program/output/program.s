.text
.globl main

main:
    move $fp, $sp

    li $t0, 314
    sw $t0, -4($fp)
    lw $t0, -4($fp)
    sw $t0, -8($fp)
    lw $t0, -12($fp)
    sw $t0, -4($fp)
    lw $t0, -4($fp)
    sw $t0, -4($fp)
    lw $t0, -16($fp)
    sw $t0, -4($fp)
    lw $t0, -4($fp)
    sw $t0, -13($fp)
    lw $t0, -20($fp)
    sw $t0, -4($fp)
    lw $t0, -4($fp)
    sw $t0, -29($fp)
    lw $t0, -24($fp)
    sw $t0, -4($fp)
    li $t1, 1
    sw $t1, -28($fp)
    lw $t2, -4($fp)
    lw $t3, -28($fp)
    add $t4, $t2, $t3
    sw $t4, -32($fp)
    lw $v0, -32($fp)
    jr $ra
    li $t1, 5
    sw $t1, -28($fp)
    lw $t1, -28($fp)
    sw $t1, -16($fp)
    addi $sp, $sp, -4
    sw $fp, 0($sp)
    addi $sp, $sp, -0
    move $fp, $sp
    jal makeAdder
    move $t1, $v0
    sw $t1, -28($fp)
    move $sp, $fp
    lw $fp, 0($sp)
    addi $sp, $sp, 4
    # store None → FP[45]
    lw $t0, -36($fp)
    sw $t0, -4($fp)
    lw $t5, -45($fp)
    sw $t5, -40($fp)
    lw $t6, -4($fp)
    lw $t7, -40($fp)
    add $t8, $t6, $t7
    sw $t8, -44($fp)
    lw $t9, -44($fp)
    move $a0, $t9
    li $v0, 1
    syscall
    lw $t8, -45($fp)
    sw $t8, -44($fp)
    li $t5, 5
    sw $t5, -40($fp)
    lw $t0, -44($fp)
    lw $t1, -40($fp)
    slt $t2, $t1, $t0
    sw $t2, -4($fp)
    lw $t2, -4($fp)
    beq $t2, $zero, L2
L1:
    lw $t2, -48($fp)
    sw $t2, -4($fp)
    lw $t9, -4($fp)
    move $a0, $t9
    li $v0, 1
    syscall
    j L3
L2:
    lw $t2, -52($fp)
    sw $t2, -4($fp)
    lw $t9, -4($fp)
    move $a0, $t9
    li $v0, 1
    syscall
L3:
L4:
    lw $t2, -45($fp)
    sw $t2, -4($fp)
    li $t5, 10
    sw $t5, -40($fp)
    lw $t4, -4($fp)
    lw $t5, -40($fp)
    slt $t8, $t4, $t5
    sw $t8, -44($fp)
    lw $t8, -44($fp)
    beq $t8, $zero, L5
    lw $t8, -45($fp)
    sw $t8, -44($fp)
    li $t7, 1
    sw $t7, -40($fp)
    lw $t8, -44($fp)
    lw $t9, -40($fp)
    add $t2, $t8, $t9
    sw $t2, -4($fp)
    lw $t2, -4($fp)
    sw $t2, -45($fp)
    j L4
L5:
L6:
    lw $t2, -56($fp)
    sw $t2, -4($fp)
    lw $t7, -45($fp)
    sw $t7, -40($fp)
    lw $t0, -4($fp)
    lw $t1, -40($fp)
    add $t2, $t0, $t1
    sw $t2, -44($fp)
    lw $t3, -44($fp)
    move $a0, $t3
    li $v0, 1
    syscall
    lw $t2, -45($fp)
    sw $t2, -44($fp)
    li $t7, 1
    sw $t7, -40($fp)
    lw $t8, -44($fp)
    lw $t9, -40($fp)
    sub $t4, $t8, $t9
    sw $t4, -4($fp)
    lw $t4, -4($fp)
    sw $t4, -45($fp)
    lw $t4, -45($fp)
    sw $t4, -4($fp)
    li $t7, 7
    sw $t7, -40($fp)
    lw $t5, -4($fp)
    lw $t6, -40($fp)
    slt $t2, $t6, $t5
    sw $t2, -44($fp)
    lw $t2, -44($fp)
    bne $t2, $zero, L6
L7:
    li $t2, 0
    sw $t2, -44($fp)
    lw $t2, -44($fp)
    sw $t2, -60($fp)
L8:
    lw $t2, -60($fp)
    sw $t2, -44($fp)
    li $t8, 3
    sw $t8, -40($fp)
    lw $t9, -44($fp)
    lw $t0, -40($fp)
    slt $t4, $t9, $t0
    sw $t4, -4($fp)
    lw $t4, -4($fp)
    beq $t4, $zero, L9
    lw $t4, -64($fp)
    sw $t4, -4($fp)
    lw $t8, -60($fp)
    sw $t8, -40($fp)
    lw $t2, -4($fp)
    lw $t3, -40($fp)
    add $t4, $t2, $t3
    sw $t4, -44($fp)
    lw $t5, -44($fp)
    move $a0, $t5
    li $v0, 1
    syscall
L10:
    lw $t4, -60($fp)
    sw $t4, -44($fp)
    lw $t8, -60($fp)
    sw $t8, -40($fp)
    li $t6, 1
    sw $t6, -4($fp)
    lw $t7, -40($fp)
    lw $t8, -4($fp)
    add $t9, $t7, $t8
    sw $t9, -68($fp)
    j L8
L9:
    lw $t9, -13($fp)
    sw $t9, -68($fp)
    li $t6, 0
    sw $t6, -4($fp)
    lw $t0, -68($fp)
    move $a0, $t0
    jal cs_array_len
    move $t1, $v0
    sw $t1, -40($fp)
L11:
    lw $t2, -4($fp)
    lw $t3, -40($fp)
    slt $t5, $t2, $t3
    xori $t4, $t5, 1
    sw $t4, -72($fp)
    lw $t4, -72($fp)
    bne $t4, $zero, L12
    lw $t6, -68($fp)
    lw $t7, -4($fp)
    move $a0, $t6
    move $a1, $t7
    jal cs_array_get
    move $t1, $v0
    sw $t1, -40($fp)
    lw $t1, -40($fp)
    sw $t1, -76($fp)
    lw $t8, -76($fp)
    sw $t8, -4($fp)
    li $t8, 3
    sw $t8, -4($fp)
    lw $t9, -4($fp)
    lw $t0, -4($fp)
    sub $t2, $t9, $t0
    sltiu $t1, $t2, 1
    sw $t1, -80($fp)
    lw $t1, -80($fp)
    beq $t1, $zero, L15
L14:
    j L13
L15:
    lw $t1, -84($fp)
    sw $t1, -80($fp)
    lw $t8, -76($fp)
    sw $t8, -4($fp)
    lw $t3, -80($fp)
    lw $t4, -4($fp)
    add $t5, $t3, $t4
    sw $t5, -88($fp)
    lw $t6, -88($fp)
    move $a0, $t6
    li $v0, 1
    syscall
    lw $t5, -76($fp)
    sw $t5, -88($fp)
    li $t8, 4
    sw $t8, -4($fp)
    lw $t9, -88($fp)
    lw $t0, -4($fp)
    slt $t1, $t0, $t9
    sw $t1, -80($fp)
    lw $t1, -80($fp)
    beq $t1, $zero, L18
L17:
    j L12
L18:
L13:
    li $t1, 1
    sw $t1, -80($fp)
    lw $t7, -4($fp)
    lw $t8, -80($fp)
    add $t9, $t7, $t8
    sw $t9, -4($fp)
    lw $t9, -4($fp)
    sw $t9, -4($fp)
    j L11
L12:
    lw $t0, -45($fp)
    sw $t0, -68($fp)
    li $t9, 7
    sw $t9, -4($fp)
    lw $t5, -92($fp)
    sw $t5, -88($fp)
    lw $t6, -88($fp)
    move $a0, $t6
    li $v0, 1
    syscall
    li $t5, 6
    sw $t5, -88($fp)
    lw $t1, -96($fp)
    sw $t1, -100($fp)
    lw $t6, -100($fp)
    move $a0, $t6
    li $v0, 1
    syscall
    lw $t1, -104($fp)
    sw $t1, -100($fp)
    lw $t6, -100($fp)
    move $a0, $t6
    li $v0, 1
    syscall
    la  $a0, L20
    jal cs_push_handler
    lw $t1, -13($fp)
    sw $t1, -100($fp)
    li $t2, 10
    sw $t2, -108($fp)
    lw $t3, -100($fp)
    lw $t4, -108($fp)
    move $a0, $t3
    move $a1, $t4
    jal cs_array_get
    move $t5, $v0
    sw $t5, -112($fp)
    lw $t5, -112($fp)
    sw $t5, -116($fp)
    lw $t5, -120($fp)
    sw $t5, -112($fp)
    lw $t6, -116($fp)
    sw $t6, -124($fp)
    lw $t7, -112($fp)
    lw $t8, -124($fp)
    add $t9, $t7, $t8
    sw $t9, -128($fp)
    lw $t0, -128($fp)
    move $a0, $t0
    li $v0, 1
    syscall
    jal cs_pop_handler
    # catch_begin err, L22
    lw $t9, -132($fp)
    sw $t9, -128($fp)
    lw $t6, -136($fp)
    sw $t6, -124($fp)
    lw $t1, -128($fp)
    lw $t2, -124($fp)
    add $t5, $t1, $t2
    sw $t5, -112($fp)
    lw $t0, -112($fp)
    move $a0, $t0
    li $v0, 1
    syscall
    j L21
    # alloc Animal -> t12
    li $a0, 0   # [TODO] type_id para objetos
    jal cs_alloc_object
    move $t5, $v0
    sw $t5, -112($fp)
    lw $t5, -112($fp)
    sw $t5, -140($fp)
    lw $t6, -144($fp)
    sw $t6, -124($fp)
    lw $t6, -124($fp)
    sw $t6, -148($fp)
    lw $t5, -112($fp)
    sw $t5, -152($fp)
    lw $t5, -112($fp)
    sw $t5, -112($fp)
    # getprop t12.name -> t14
    lw $t3, -112($fp)
    li $a1, 0   # [TODO] prop_id para campos
    move $a0, $t3
    jal cs_getprop
    move $t9, $v0
    sw $t9, -128($fp)
    lw $t4, -156($fp)
    sw $t4, -160($fp)
    lw $t5, -128($fp)
    lw $t6, -160($fp)
    add $t7, $t5, $t6
    sw $t7, -164($fp)
    lw $v0, -164($fp)
    jr $ra
    # alloc Dog -> t15
    li $a0, 0   # [TODO] type_id para objetos
    jal cs_alloc_object
    move $t4, $v0
    sw $t4, -160($fp)
    lw $t4, -160($fp)
    sw $t4, -168($fp)
    lw $t9, -160($fp)
    sw $t9, -128($fp)
    # getprop t14.name -> t17
    lw $t8, -128($fp)
    li $a1, 0   # [TODO] prop_id para campos
    move $a0, $t8
    jal cs_getprop
    move $t9, $v0
    sw $t9, -172($fp)
    lw $t0, -176($fp)
    sw $t0, -180($fp)
    lw $t1, -172($fp)
    lw $t2, -180($fp)
    add $t3, $t1, $t2
    sw $t3, -184($fp)
    lw $v0, -184($fp)
    jr $ra
    lw $t0, -188($fp)
    sw $t0, -180($fp)
    # store None → FP[49]
    lw $t9, -49($fp)
    sw $t9, -172($fp)
    # getprop t17.speak -> t20
    lw $t4, -172($fp)
    li $a1, 0   # [TODO] prop_id para campos
    move $a0, $t4
    jal cs_getprop
    move $t5, $v0
    sw $t5, -192($fp)
    jal t20
    lw $t6, -196($fp)
    move $a0, $t6
    li $v0, 1
    syscall
    lw $t7, -13($fp)
    sw $t7, -196($fp)
    li $t8, 0
    sw $t8, -200($fp)
    lw $t9, -196($fp)
    lw $t0, -200($fp)
    move $a0, $t9
    move $a1, $t0
    jal cs_array_get
    move $t1, $v0
    sw $t1, -204($fp)
    lw $t1, -204($fp)
    sw $t1, -57($fp)
    lw $t1, -208($fp)
    sw $t1, -204($fp)
    lw $t2, -57($fp)
    sw $t2, -212($fp)
    lw $t3, -204($fp)
    lw $t4, -212($fp)
    add $t5, $t3, $t4
    sw $t5, -216($fp)
    lw $t6, -216($fp)
    move $a0, $t6
    li $v0, 1
    syscall
    lw $t5, -220($fp)
    sw $t5, -216($fp)
    lw $t5, -216($fp)
    sw $t5, -224($fp)
    lw $t5, -224($fp)
    sw $t5, -216($fp)
    lw $v0, -216($fp)
    jr $ra
    li $t2, 2
    sw $t2, -212($fp)
    lw $t2, -212($fp)
    sw $t2, -16($fp)
    addi $sp, $sp, -4
    sw $fp, 0($sp)
    addi $sp, $sp, -16
    move $fp, $sp
    jal getMultiples
    move $t2, $v0
    sw $t2, -212($fp)
    move $sp, $fp
    lw $fp, 0($sp)
    addi $sp, $sp, 4
    lw $t2, -212($fp)
    sw $t2, -61($fp)
    lw $t2, -228($fp)
    sw $t2, -212($fp)
    lw $t1, -61($fp)
    sw $t1, -204($fp)
    li $t6, 0
    sw $t6, -232($fp)
    lw $t9, -204($fp)
    lw $t0, -232($fp)
    move $a0, $t9
    move $a1, $t0
    jal cs_array_get
    move $t7, $v0
    sw $t7, -236($fp)
    lw $t8, -212($fp)
    lw $t9, -236($fp)
    add $t0, $t8, $t9
    sw $t0, -240($fp)
    lw $t7, -244($fp)
    sw $t7, -236($fp)
    lw $t1, -240($fp)
    lw $t2, -236($fp)
    add $t3, $t1, $t2
    sw $t3, -212($fp)
    lw $t7, -61($fp)
    sw $t7, -236($fp)
    li $t0, 1
    sw $t0, -240($fp)
    lw $t4, -236($fp)
    lw $t5, -240($fp)
    move $a0, $t4
    move $a1, $t5
    jal cs_array_get
    move $t6, $v0
    sw $t6, -248($fp)
    lw $t7, -212($fp)
    lw $t8, -248($fp)
    add $t9, $t7, $t8
    sw $t9, -252($fp)
    lw $t0, -252($fp)
    move $a0, $t0
    li $v0, 1
    syscall
    lw $t9, -76($fp)
    sw $t9, -252($fp)
    li $t6, 1
    sw $t6, -248($fp)
    lw $t1, -252($fp)
    lw $t2, -248($fp)
    slt $t3, $t2, $t1
    xori $t3, $t3, 1
    sw $t3, -212($fp)
    lw $t4, -212($fp)
    beq $t4, $zero, L24
L23:
    li $t4, 1
    sw $t4, -212($fp)
    lw $v0, -212($fp)
    jr $ra
L24:
    lw $t6, -76($fp)
    sw $t6, -248($fp)
    lw $t9, -76($fp)
    sw $t9, -252($fp)
    li $t5, 1
    sw $t5, -256($fp)
    lw $t6, -252($fp)
    lw $t7, -256($fp)
    sub $t8, $t6, $t7
    sw $t8, -260($fp)
    lw $t8, -260($fp)
    sw $t8, -16($fp)
    addi $sp, $sp, -4
    sw $fp, 0($sp)
    addi $sp, $sp, -0
    move $fp, $sp
    jal factorial
    move $t8, $v0
    sw $t8, -260($fp)
    move $sp, $fp
    lw $fp, 0($sp)
    addi $sp, $sp, 4
    lw $t9, -248($fp)
    lw $t0, -260($fp)
    mul $t5, $t9, $t0
    sw $t5, -256($fp)
    lw $v0, -256($fp)
    jr $ra
    lw $t8, -264($fp)
    sw $t8, -260($fp)
    lw $t1, -260($fp)
    move $a0, $t1
    li $v0, 1
    syscall
    li $v0, 10
    syscall