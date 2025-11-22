// Prueba de Arreglos básicos (Heap allocation & Indexing)
// Prueba de Clases básicas (Instanciación, atributos y métodos simples)

let arr: integer[] = [10, 20, 30, 40, 50];

print(arr[0]); // Debería imprimir 10
print(arr[2]); // Debería imprimir 30

arr[1] = 99;
print(arr[1]); // Debería imprimir 99

class Point {
    let x: integer;
    let y: integer;

    function init(newX: integer, newY: integer) {
        this.x = newX;
        this.y = newY;
    }

    function sum(): integer {
        return this.x + this.y;
    }
}

let p1: Point = new Point();

p1.x = 5;
p1.y = 10;

print(p1.x); // 5

p1.init(100, 200); 

print(p1.x); // 100

let total: integer = p1.sum();
print(total); // 300