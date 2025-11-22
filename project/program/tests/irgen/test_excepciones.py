def test_try_catch(build_ir):
    code = """
    try {
        var x: integer = 10 / 0;
    } catch (err) {
        print("Error");
    }
    """
    quads = build_ir(code)

    # A try/catch must generate: push_handler, pop_handler, and get_exception
    ops = [q.op for q in quads]

    assert "push_handler" in ops, "El IR no generó push_handler para iniciar el try"
    assert "pop_handler" in ops, "El IR no generó pop_handler para cerrar el try"
    assert "get_exception" in ops, "El IR no generó get_exception en el catch"
