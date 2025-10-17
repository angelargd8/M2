const PI: integer = 314;
let greeting: string = "Hello, Compiscript!";
let flag: boolean;
let numbers: integer[] = [1, 2, 3, 4, 5];
let matrix: integer[][] = [[1, 2], [3, 4]];

// Simple closure-style function (no nested type signatures)
function makeAdder(x: integer): integer {
  return x + 1;
}


let addFive: integer = (makeAdder(5));
print("5 + 1 = " + addFive);
if (addFive > 5) { print("Greater than 5"); } else { print("5 or less"); }
