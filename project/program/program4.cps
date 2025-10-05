// ==========================
// Tests: call, &&, foreach
// ==========================

// --- helpers para impresión clara ---
function sep(title: string): integer {
  print("---- " + title + " ----");
  return 0;
}

// ==========================
// 1) CALL (llamadas a función)
// ==========================
const one: integer = 1;
const two: integer = 2;

function add(x: integer, y: integer): integer {
  return x + y;
}

function mul(x: integer, y: integer): integer {
  return x * y;
}

function inc(x: integer): integer {
  return x + 1;
}

// Llamadas anidadas y con varios parámetros
let call_ok_1: integer = add(one, two);                // 1) simple → 3
let call_ok_2: integer = add(add(1, 2), add(3, 4));    // 2) anidada → 10
let call_ok_3: integer = mul(inc(4), add(2, 3));       // 3) compuesta → (5 * 5) = 25

sep("CALL");
print("call_ok_1 = " + call_ok_1); // esperado: 3
print("call_ok_2 = " + call_ok_2); // esperado: 10
print("call_ok_3 = " + call_ok_3); // esperado: 25


// =======================================
// 2) && y || con CORTOCIRCUITO (side effects)
// =======================================

// contador global para verificar si se evalúa RHS
let ticks: integer = 0;

function tickTrue(label: string): boolean {
  ticks = ticks + 1;
  print("tickTrue(" + label + ")");
  return true;
}

function tickFalse(label: string): boolean {
  ticks = ticks + 1;
  print("tickFalse(" + label + ")");
  return false;
}

sep("&& / || SHORT-CIRCUIT");

// Caso A: false && tickTrue(...)  → NO debe llamar RHS
ticks = 0;
let A: boolean = (1 < 0) && tickTrue("A");
print("A = " + A);               // esperado: false
print("ticks = " + ticks);       // esperado: 0

// Caso B: true || tickTrue(...)  → NO debe llamar RHS
ticks = 0;
let B: boolean = (2 > 1) || tickTrue("B");
print("B = " + B);               // esperado: true
print("ticks = " + ticks);       // esperado: 0

// Caso C: true && tickTrue(...)  → SÍ debe llamar RHS una vez
ticks = 0;
let C: boolean = (5 == 5) && tickTrue("C");
print("C = " + C);               // esperado: true
print("ticks = " + ticks);       // esperado: 1

// Caso D: false || tickTrue(...) → SÍ debe llamar RHS una vez
ticks = 0;
let D: boolean = (3 < 0) || tickTrue("D");
print("D = " + D);               // esperado: true
print("ticks = " + ticks);       // esperado: 1

// Caso E: composición: (false && tickTrue) || (true && tickTrue) → solo se llama el segundo tick
ticks = 0;
let E: boolean = ((0 == 1) && tickTrue("E-left")) || ((1 == 1) && tickTrue("E-right"));
print("E = " + E);               // esperado: true
print("ticks = " + ticks);       // esperado: 1


// ==========================
// 3) FOREACH (listas, continue/break)
// ==========================
sep("FOREACH");

let numbers: integer[] = [1, 2, 3, 4, 5];

// Básico con continue y break
foreach (n in numbers) {
  if (n == 3) {
    print("skip " + n);
    continue;                    // salta el 3
  }
  print("n = " + n);
  if (n > 4) {
    print("break at " + n);
    break;                       // se detiene al pasar 4 (imprime 5 y rompe)
  }
}

// Foreach sobre arreglo vacío (no debe imprimir nada dentro del bucle)
let empty: integer[] = [];
print("empty-begin");
foreach (e in empty) {
  print("should-not-print");
}
print("empty-end");

// Foreach anidado en matriz (2D)
let matrix: integer[][] = [[1, 2], [3, 4]];
foreach (row in matrix) {
  foreach (v in row) {
    print("m = " + v);
  }
}

// Foreach que acumula
function sumArray(xs: integer[]): integer {
  let acc: integer = 0;
  foreach (k in xs) {
    acc = acc + k;
  }
  return acc;
}

let s123: integer = sumArray([1, 2, 3]);   // → 6
print("sum([1,2,3]) = " + s123);

// Fin
print("DONE");
