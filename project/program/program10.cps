// Simple closure-style function (no nested type signatures)
function makeAdder(x: integer): integer {
  return x + 1;
}

let addFive: integer = (makeAdder(5));
print("5 + 1 = " );
print(addFive);

