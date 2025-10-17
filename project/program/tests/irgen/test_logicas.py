# expresiones logicas
def test_expresiones_logicas(build_ir):
    code = """
    var a: boolean = 5 < 10 && true;
    var b: boolean = a || false;
    """
    quads = build_ir(code)

    ops = [q.op for q in quads]
    assert "<" in ops, "Falta comparación <"
    assert "&&" in ops, "Falta operación lógica AND"
    assert "||" in ops, "Falta operación lógica OR"
