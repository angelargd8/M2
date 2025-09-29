let flag: boolean = true;

// Condiciones deben ser boolean
if (flag) {
    print("Flag es verdadero");
}

// while con condición boolean
let i: integer = 0;
while (i < 5) {  // ✅ i<5 es boolean
    i = i + 1;
}

// do-while
do {
    i = i - 1;
} while (i > 0);


for (let j: integer = 0; j < 5; j = j + 1) {
    if (j == 2) { 
        continue;  // ✅ ahora dentro de un bloque
    }
    if (j == 4) { 
         break; 
     }
}

// return sólo dentro de funciones
function foo(): integer {
    return 10;              // ✅ correcto
}
// return 5;                // ❌ error: return fuera de función
