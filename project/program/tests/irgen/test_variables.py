def test_variable_declaration_and_assignment(build_ir):
    code = """
    var x: integer = 10;
    var y: integer = 20;
    x = y;
    """
    quads = build_ir(code)
    print(quads)

    ops = [q.op for q in quads]

    assert "copy" in ops, "No se generaron instrucciones copy"

    # Se asigna 10 a alguna variable temporal
    assert any(q.op == "copy" and q.a == 10 for q in quads), "No se encontró asignación del valor 10"

    # Se asigna 20 a alguna variable temporal
    assert any(q.op == "copy" and q.a == 20 for q in quads), "No se encontró asignación del valor 20"

    assert any("t3" == q.a and "t2" == q.result for q in quads), \
         "No se copió correctamente y en x"
