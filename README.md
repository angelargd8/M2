# [M2] Fase de Compilación: Generación de Código Intermedio

## Descripción del proyecto:
La generación de código intermedio (CI) es la siguiente fase del diseño de nuestro compilador de Compiscript. Luego de haber realizado el análisis semántico (análisis de tipos), utilizarán sus estructuras de datos (árboles sintácticos, tablas de símbolos) para generar una representación intermedia del código de alto nivel. Esta representación intermedia les será de utilidad al momento de la generación de código assembler (u objeto).

En el directorio program encontrará la gramática de este lenguaje en ANTLR y en BNF. Se le otorga un playground similar a los laboratorios para que usted pueda experimentar inicialmente.


- Gramáticas ANTLR (.g4) para definir la sintaxis del lenguaje. 
- Archivos generados por ANTLR (Lexer, Parser, Visitor, Listener) para procesar el código fuente. 
- Un AST (Árbol de Sintaxis Abstracta) construido con clases dataclass en AstNodes.py. 
- AstBuilder que transforma el árbol de ANTLR en el AST propio. 
- SemanticAnalyzer que realiza el chequeo semántico: verifica tipos, ámbitos, herencia, declaraciones, y reporta errores semánticos. 
- Una SymbolTable que gestiona los símbolos (variables, funciones, tipos) y los distintos scopes. 
- Visualización del AST con Graphviz . 
- Driver: parsea el código, construye el AST, lo visualiza y ejecuta el análisis semántico. 


## 🧰 Instrucciones de Configuración

1. **Construir y Ejecutar el Contenedor Docker:** Desde el directorio raíz, ejecuta el siguiente comando para construir la imagen y lanzar un contenedor interactivo:

```bash
docker build --rm . -t csp-image
docker run -ti -v "$(pwd)/program":/program -p 8501:8501 csp-image
```

volverlo a correr
```bash
cd ~/compis/M2/project
docker run --rm -it -v "$(pwd)":/program -w /program csp-image
```

Abrir un nuevo cmd
Usar usuario root de docker
```
docker exec -it --user root <container id> bash
apt update
apt install graphviz
apt install python3.12-venv
```

Regresar al shell de appuser
activar en venv en el container:
```
python3 -m venv .venv
. .venv/bin/activate
```
Version de python:
```
Python 3.12.3
```

instalar antlr:
```
python -m pip install --upgrade pip
pip install -r requirements.txt 
pip install streamlit

#comprobar que se instalo:
which python
python -c "import antlr4; print('ANTLR runtime OK')"
```

Correr el IDE:
- requerimientos: 
tener instalado streamlit:
```
pip install streamlit
```
y pytest:
```
pip install pytest
```

Correr un test:
```
pytest -v -s tests/irgen/test_arreglos.py
```
Correr todos los test:
```
pytest -v -s tests/irgen/
```

Cambiar al shell root user 
```
. .venv/bin/activate
streamlit run app.py
```
Como correr el programa en la consola:
```
cd project
. .venv/bin/activate
python Driver.py program.cps
```

---


```
docker run --rm -u "$UIDGID" -v "$(pwd)":/work -w /work csp-image bash -lc 'java -jar /usr/local/lib/antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor -no-listener -o program/gen program/Compiscript.g4'
```



Como correr el programa:
python Driver.py program.cps




## 📋 Requerimientos


* Agregar acciones semánticas necesarias sobre el árbol sintáctico construido, con el objetivo de generar código intermedio. La sintáxis del código intermedio a utilizar es a discreción del diseñador (pueden utilizar la sintáxis de alguna bibliografía conocida o la vista en clase).

* Complementar la información de la tabla de símbolos con datos necesarios para la generación de código assembler u objeto (direcciones de memoria, etiquetas temporales, etc.)

* Implementar un algoritmo para asignación y reciclaje de variables temporales durante la transformación de expresiones aritméticas.

* **Para los puntos anteriores, deberá de escribir una batería de tests para validar casos exitosos y casos fallidos en cada una de los casos que crea convenientes.**

* Al momento de presentar su trabajo, esta batería de tests debe estar presente y será tomada en cuenta para validar el funcionamiento de su compilador.

* Editar la implementación de la **tabla de símbolos** que interactue con cada fase de la compilación, para soportar los ambientes y entornos en tiempo de ejecución, utilizando registros de activación.

* Deberá **desarrollar un IDE** que permita a los usuarios escribir su propio código y compilarlo.


---
### Requerimientos del M1:

🟢✅ 1. **Crear un analizador sintáctico utilizando ANTLR** o cualquier otra herramienta similar de su elección
   * Se recomienda usar ANTLR dado que es la herramienta que se utiliza en las lecciones del curso, pero puede utilizar otro Generador de Parsers.

**Analizador léxico:** CompiscriptLexer -> convierte texto -> tokens

**Analizador sintactico:** CompiscriptParser -> tokens -> arbol de parseo

**Analizador sintactico:** tree = parser.program(). A partir de los tokens que produce el lexer y de una gramatica, verifica que la secuencia cumpla con la sintaxis del lenguaje y construye una estructura jerarquja, que en este caso es el arbol de parseo.

-------

2. Añadir **acciones/reglas semánticas** en este analizador sintáctico y **construir un  ́****arbol sintáctico, con una representación visual****.**
   1. **Sistema de Tipos**
      * 🟢 Verificación de tipos en operaciones aritméticas (`+`, `-`, `*`, `/`) — los operandos deben ser de tipo `integer` o `float`.
      *  Verificación de tipos en operaciones lógicas (`&&`, `||`, `!`) — los operandos deben ser de tipo `boolean`.
      * 🟢 Compatibilidad de tipos en comparaciones (`==`, `!=`, `<`, `<=`, `>`, `>=`) — los operandos deben ser del mismo tipo compatible.
      * 🟢 Verificación de tipos en asignaciones — el tipo del valor debe coincidir con el tipo declarado de la variable.
      *  Inicialización obligatoria de constantes (`const`) en su declaración.
      * 🟢 Verificación de tipos en listas y estructuras (si se soportan más adelante).
   2. **Manejo de Ámbito**
      * 🟢 Resolución adecuada de nombres de variables y funciones según el ámbito local o global.
      * 🟢 Error por uso de variables no declaradas.
      * 🟢 Prohibir redeclaración de identificadores en el mismo ámbito.
      * 🟢 Control de acceso correcto a variables en bloques anidados.
      * 🟢 Creación de nuevos entornos de símbolo para cada función, clase y bloque.
   3. **Funciones y Procedimientos**
      * 🟢 Validación del número y tipo de argumentos en llamadas a funciones (coincidencia posicional).
      * 🟢 Validación del tipo de retorno de la función — el valor devuelto debe coincidir con el tipo declarado.
      * 🟢 Soporte para funciones recursivas — verificación de que pueden llamarse a sí mismas.
      * 🟢 Soporte para funciones anidadas y closures — debe capturar variables del entorno donde se definen.
      * 🟢 Detección de múltiples declaraciones de funciones con el mismo nombre (si no se soporta sobrecarga).
      
   4. **Control de Flujo**
      * 🟢 Las condiciones en `if`, `while`, `do-while`, `for`, `switch` deben evaluar expresiones de tipo `boolean`.
      * 🟢 Validación de que se puede usar `break` y `continue` sólo dentro de bucles.
      * 🟢 Validación de que el `return` esté dentro de una función (no fuera del cuerpo de una función).
   5. **Clases y Objetos**
      * 🟢 Validación de existencia de atributos y métodos accedidos mediante `.` (dot notation).
      * 🟢 Verificación de que el constructor (si existe) se llama correctamente.
      * 🟢 Manejo de `this` para referenciar el objeto actual (verificar ámbito).
   6. **Listas y Estructuras de Datos**
      * 🟢 Verificación del tipo de elementos en listas.
      * 🟢 Validación de índices (acceso válido a listas).
   7. **Generales**
      * 🟢 Detección de código muerto (instrucciones después de un `return`, `break`, etc.).
      * 🟢 Verificación de que las expresiones tienen sentido semántico (por ejemplo, no multiplicar funciones).
      * 🟢 Validación de declaraciones duplicadas (variables, parámetros).
3. Implementar la recorrida de este árbol utilizando ANTLR Listeners o Visitors para evaluar las reglas semánticas que se ajusten al lenguaje.
4. **Para los puntos anteriores, referentes a las reglas semánticas, deberá de escribir una batería de tests para validar casos exitosos y casos fallidos en cada una de las reglas mencionadas.**
   * Al momento de presentar su trabajo, esta batería de tests debe estar presente y será tomada en cuenta para validar el funcionamiento de su compilador.
5. Construir una **tabla de símbolos** que interactue con cada fase de la compilación, incluyendo las fases mencionadas anteriormente. Esta tabla debe considerar el **manejo de entornos** y almacenar toda la información necesaria para esta y futuras fases de compilación.
6. Deberá **desarrollar un IDE** que permita a los usuarios escribir su propio código y compilarlo.
7. Deberá crear **documentación asociada a la arquitectura de su implementación** y **documentación de las generalidades de cómo ejecutar su compilador**.
-----------

**Driver:**

El proyecto empieza en el driver, allí es donde lee el archivo de compiscript, luego se usa ANTLR para hacer el análisis léxico y sintactico para generar el árbol de parseo, y si hay errores de sintaxis los muestra y termina el programa. Luego se convierte el árbol de parseo en un AST usando AstBuilder, se guarda el AST en output. 

Ya luego se crea un semanticAnalyzer y hay dos pasadas,  

La primera recolecta firmas de funciones, clases y propiedades 

Y en la segunda pasada se revisan las reglas semánticas, como tipos, ámbitos o como herencia. Y si hay errores semánticos los muestra y sino indica que el chequeo no tiene errores. 

 

**AstBuilder:** 

Se define la clase AstBuilder que lo que hace es extender el visitor generado por ANTLR para transformar el parse tree en un AST.  

Las funciones de este archivo son: 

Mapear los nodos del parse tree a las clases dataclass que están en AstNonde 

Implementar métodos Visit para cada tipo de nodo del lenguaje, como declaraciones 

Convierte los tipos textuales del lenguaje fuente a tipos internod como de integer a int 

Procesa declaraciones de variables, constantes, funciones, acceso a miembros, literales y estructuras de control 

 

**AstNodes:**

Se definen todas las clases de nodos que forman el AST y se sa las dataclases para la definición de las estructuras de datos. 

Cada clase aqui representa un tipo de nodo en el AST, como declaraciones, sentencias, expresiones y los nodos tienen atributos que corresponden a los elementos sintacticos del lenguaje. 

 

**SymbolTable:** 

Implementa la tabla de símbolos y los alcances para el analisis semántico del lenguaje 

El TypeSymbol: representa un tipo 

VarableSymbol: representa una variable con nombre, tipo, si es constante, inicializada y referencia al nodo de declaraci[on 

Scope:  el alcance con símbolos definidos y referencia el scope padre, este permite definir y resolver símbolos en la cadena de scopes 

SymbolTable: administra los scopes y los tipos, tiene el scope global el actual y los metodos para crear, entrar y salir de scopes, define y resulve variables y funciones y obtiene los tipos. 

**SemanticAnalyzer:** 
Implementa el analizador semántico para el lenguaje de Compiscript su función es verificar que el programa sea correcto a nivel de tipos, ámbitos, herencia y reglas semánticas.  
Los métodos de utilidades son para agregar errores, verificar tipos, herencia y propiedades 
Tiene dos pasadas principales: 

- Collect_signatures: que recolecta firmas de funciones, métodos y clases y construye la información de herencia y propiedades 
- Check: recorre el AST y válida las reglas semánticas (como tipos, inicialización...)  

Los métodos _visit_ para cada tipo del nodo de AST realiza las validaciones correspondientes, como declaraciones, asignaciones, control de flujo, expresiones.  
Y reporta errores semánticos con información de la línea y columna.  
