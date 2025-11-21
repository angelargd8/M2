
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

// break and continue control secuence 
print("==break - continue ==");

for (var p = 0; p < 10; p = p + 1) {

    if (p == 3) {
        print("continue at p = 3");
        continue;
    }

    if (p == 7) {
        print("break at p = 7");
        break;
    }

    print("p = " + p);
}


// switch and continue control secuence 
print("==switch==");

var day = 3;

switch (day) {
    case 1:
        print("Monday");
    case 2:
        print("Tuesday");
    case 3:
        print("Wednesday");
    default:
        print("Unknown day");
}

