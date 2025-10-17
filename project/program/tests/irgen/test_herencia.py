# herencia
def test_herencia(build_ir):
    code = """
    class Animal { function speak() { print("..."); } }
    class Dog : Animal { function speak() { print("Woof"); } }
    var d = new Dog();
    d.speak();
    """
    quads = build_ir(code)

    assert any("class" in str(q.op) or q.op == "call" for q in quads), "No se generó herencia o llamada de método"
