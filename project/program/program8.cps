// ======= ARITMETIC OPERATIONS ========

print("==SUMA==");
function makeAdder(x: integer): integer {
  return x + 2;
}
let addFive: integer = (makeAdder(5));
print("5 + 2 = " );
print(addFive);


print("==RESTA==");
function RESTA(x: integer): integer {
  return x - 2;
}
let restar: integer = (RESTA(5));
print("5 - 2 = " );
print(restar);

print("==MULTIPLICACION==");
function MULTIPLICACION(x: integer): integer {
  return x * 2;
}
let multiplicar: integer = (MULTIPLICACION(5));
print("5 * 2 = " );
print(multiplicar);

print("==DIVISION==");
function DIVISION(x: float): float {
  return x / 2.0;
}
let dividir: float = (DIVISION(5));
print("5 / 2 = " );
print(dividir);