# while y for
def test_if_while_for(build_ir):
    code = """
    var x: integer = 0;
    if (x < 5) { print(x); }
    while (x < 3) { x = x + 1; }
    for (var i = 0; i < 3; i = i + 1) { print(i); }
    """
    quads = build_ir(code)

    assert any(q.op.startswith("if") for q in quads), "Falta salto condicional"
    assert any(q.op == "goto" for q in quads), "Faltan saltos de bucle"
    assert any(q.op == "label" for q in quads), "Faltan etiquetas de control"
