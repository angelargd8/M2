print("==TRY-CATCH simple==");

try {
    var x = 10;
    var y = 0;
    var z = x / y;     // Fuerza error
    print("NO DEBERÍA VERSE");
} catch (e) {
    print("Caught an error:");
    print(e);
}

print("end");
