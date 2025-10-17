class Point {
    let x: integer =0;
    var y: integer = 0;

    function init(a: integer, b: integer): void {
        this.x = a;
        this.y = b;
    }
}

var p = new Point();
p.init(3, 4);