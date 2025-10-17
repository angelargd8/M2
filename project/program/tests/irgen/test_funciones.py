def test_funcion_y_parametros(build_ir):
    code = """
    function add(a, b) { return a + b; }
    var result = add(3, 4);
    """
    quads = build_ir(code)

    assert any(q.op == "param" for q in quads), "No se generaron parámetros"
    assert any(q.op == "call" for q in quads), "No se generó llamada a función"
    assert any(q.op == "ret" or q.op == "move_ret" for q in quads), "Falta retorno de función"
