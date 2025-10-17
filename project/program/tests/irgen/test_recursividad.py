# recursion
def test_funcion_recursiva(build_ir):
    code = """
    function fact(n: integer): integer {
    if (n <= 1) {
        return 1;
    }
    return n * fact(n - 1);
    }
    var x: integer = fact(5);

    """
    quads = build_ir(code)

    assert any(q.op == "call" for q in quads), "Falta llamada recursiva"
    assert any(q.op == "*" for q in quads), "Falta multiplicación del factorial"
