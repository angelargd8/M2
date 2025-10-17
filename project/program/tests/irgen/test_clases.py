def test_clases_y_objetos(build_ir):
    code = """
    class Point {
        var x;
        var y;
        function init(a, b) {
            this.x = a;
            this.y = b;
        }
    }
    var p = new Point();
    p.init(3, 4);
    """
    quads = build_ir(code)

    assert any("new" in str(q.op) or q.op == "call" for q in quads), "Falta creación o llamada de método"
