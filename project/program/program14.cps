
//while control secuence 
print("==WHILE==");
var i = 0;
while (i < 5) {
    print("i = " + i);
    i = i + 1;
}

//for  control secuence 
print("==FOR==");

for (var j = 0; j < 4; j = j + 1) {
    print("j = " + j);
}

//do-while control secuence 
print("==do-while==");
var k = 0;

do {
    print("k = " + k);
    k = k + 1;
} while (k < 3);


// foreach control secuence 
print("==foreach==");
var nums = [1, 2, 3, 4];
var total = 0;

foreach (n in nums) {
    total = total + n;
}

print("Total = " + total);