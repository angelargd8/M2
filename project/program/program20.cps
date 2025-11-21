// Function returning an array
function getMultiples(n: integer): integer[] {
  let result: integer[] = [n * 1, n * 2, n * 3, n * 4, n * 5];
  return result;
}

let multiples: integer[] = getMultiples(2);
print("Multiples of 2: " + multiples[0] + "," + multiples[1]);
