let a: integer= 4;
let b: integer = 3;

let sum: integer = a + b;  

let flag1: boolean = true;
let flag2: boolean = false;

// Operaciones válidas
let resultAnd: boolean = flag1 && flag2; // false
let resultOr: boolean = flag1 || flag2;  // true
let resultNot: boolean = !flag1;         // false

let x: integer = 5;
let y: integer = 10;
let comp1: boolean = x == y;      // false
let comp2: boolean = x < y;       // true

let age: integer;
age = 25;

let name: string;
name = "Francis";  // correcto

const MAX_USERS: integer = 100;
const WELCOME_MESSAGE: string = "Bienvenidos!";

let nums: integer[] = [1, 2, 3, 4];         // lista de integers
let mixed: integer[] = [1, 2, 3];           // correcto
// let invalidList: integer[] = [1, "two"]; // error: string no es compatible con integer

let grid: integer[][] = [[1, 2], [3, 4]];   // matriz de integers