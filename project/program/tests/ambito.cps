// Variable global
let globalVar: integer = 10;

function testScope(): void {
    let localVar: integer = 5;  // Variable local

    print(globalVar); // Acceso a variable global
    print(localVar);  // Acceso a variable local

    {
        let blockVar: integer = 3;
        print(localVar);  // Se puede acceder a variable del bloque externo
        print(blockVar);  // Acceso a variable del bloque actual
    }

    // print(blockVar); // Error: blockVar no existe aquí
}

// Error por variable no declarada
// print(undeclaredVar); // Error

// Prohibir redeclaración en el mismo ámbito
let a: integer = 1;
// let a: integer = 2; // Error: redeclaración

testScope();
