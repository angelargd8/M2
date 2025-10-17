# arreglos
def test_arreglos(build_ir):
    code = """
    let arr: integer[] = [1, 2, 3];
    print(arr[1]);
    """
    quads = build_ir(code)

    assert any(q.op == "getidx" for q in quads), "No se generó getidx para acceso a arreglo"
    assert any(q.op == "print" for q in quads), "No se generó print del arreglo"
