function fact(n: integer): integer {
    if (n <= 1) {
        return 1;
    }
    return n * fact(n - 1);
}
var x: integer = fact(5);
