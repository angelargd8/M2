print("Hello world");
print(1);
print("Hello"+"Compiscript concat");

// Global constants and variables
const PI: integer = 314;
let greeting: string = "Hello, Compiscript!";
let flag: boolean;
let numbers: integer[] = [1, 2, 3, 4, 5];
let matrix: integer[][] = [[1, 2], [3, 4]];

print(PI);
print(greeting);
print(flag);
print(numbers);
print(matrix);
print("test");


//// Simple closure-style function (no nested type signatures)
//function makeAdder(x: integer): integer {
//  return x + 1;
//}
//
//let addFive: integer = (makeAdder(5));
//print("5 + 1 = " + addFive);
//