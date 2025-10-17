# expresiones aritmeticas
def test_expresiones_aritmeticas(build_ir):
    code = """
    var a: integer = 3 + 5 * 2;
    var b: integer = (a - 4) / 2;
    """
    quads = build_ir(code)

    ops = [q.op for q in quads]
    assert "*" in ops, "No se generó multiplicación"
    assert "+" in ops, "No se generó suma"
    assert "/" in ops, "No se generó división"
