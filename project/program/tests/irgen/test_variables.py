# declaracion y asignacion de variables
def test_variable_declaration_and_assignment(build_ir):
    code = """
    var x: integer = 10;
    var y: integer = 20;
    x = y;
    """
    quads = build_ir(code)

    assert any(q.op == "store" for q in quads), "No se generaron instrucciones store"
    assert any("10" in str(q.a) for q in quads), "No se encontró asignación del valor 10"
    assert any("y" in str(q.r) for q in quads), "No se asignó correctamente a y"
