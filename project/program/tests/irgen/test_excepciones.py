def test_try_catch(build_ir):
    code = """
    try {
        var x = 10 / 0;
    } catch (err) {
        print("Error");
    }
    """
    quads = build_ir(code)

    assert any("try" in str(q.op) or "catch" in str(q.op) for q in quads), \
        "Falta manejo de try/catch en el IR"
