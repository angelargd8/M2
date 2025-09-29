class Person {
    let name: string = "";
    let age: integer = 0;

    // Constructor: tipo void
    function Person(n: string, a: integer): void {
        this.name = n;
        this.age = a;
    }

    // Método
    function greet(): void {
        print("Hello, " + this.name);
    }
}

// Crear instancia correctamente sin 'new'
let p: Person;
p.Person("Francis", 20);  // llama al constructor directamente

print(p.name);   // Francis
p.greet();       // Hello, Francis
