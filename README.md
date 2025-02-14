# Construcción Directa de AFD y Ecosistema de Reconocimiento de Expresiones Regulares
Este proyecto implementa un generador de Autómatas Finitos Deterministas (AFD) a partir de expresiones regulares. La aplicación utiliza el algoritmo de construcción directa para convertir una expresión regular en un AFD, además de incluir una minimización del AFD utilizando el algoritmo de Hopcroft.

El sistema procesa una expresión regular, genera su notación postfija, construye su árbol sintáctico y visualiza tanto el árbol como el AFD resultante.

## 📁 Estructura del Proyecto
### 📂 models/
- 📄 ```regex_parser.py``` → Convierte una expresión regular en notación postfija (RPN) mediante Shunting-Yard.
- 📄 ```syntax_tree.py``` → Construye y representa el árbol sintáctico basado en la expresión postfija.
- 📄 ```dfa.py``` → Implementa la construcción de un Autómata Finito Determinista (AFD) mediante la función followpos.
- 📄 ```mindfa.py``` → Aplica el algoritmo de Hopcroft para minimizar el AFD resultante.

## 🛠 Tecnologías Utilizadas
- Python → Lenguaje principal del proyecto.
- Graphviz → Visualización de árboles sintácticos y AFDs.
- OpenAI ChatGPT → Asistencia en la generación de código para Shunting-Yard y Hopcroft.

## ⚙️ Instalación y Uso
1. **Clona el repositorio**:
    ```
   git clone <repository-url>
    ```
3. **Navega al directorio**:
   ```
   cd <repository-name>
   ```
5. **Instala las dependencias**:
    ```
   pip install graphviz
    ```
3. **Compila y ejecuta el proyecto**:
    ```
   python main.py
    ```

### Cuando se ejecute, el sistema:
1. Solicitará una expresión regular como entrada.
2. Generará la notación postfija de la expresión.
3. Construirá el árbol sintáctico y mostrará su estructura.
4. Generará el AFD y su versión minimizada.
5. Guardará las imágenes del árbol y el autómata.

## Ejemplo de Entrada y Salida
Entrada:
```(a|b)a*bb#```

Salida Esperada:

```Tokens: ['(', 'a', '|', 'b', ')', '.', 'a', '*', '.', 'b', '.', 'b', '.', '#']```

```Postfix: ['a', 'b', '|', 'a', '*', '.', 'b', '.', 'b', '.', '#', '.']```

✔ Árbol Sintáctico generado correctamente

✔ AFD y AFD Minimizado creados

## 🎥 Video demostración
[Aquí](https://youtu.be/oODn3RgnX10) puedes ver el funcionamiento del proyecto.

## 📚 Referencias
#### Sintaxis de las expresiones regulares - Ayuda de Administrador de Google Workspace
🔗[Google Workspace Support](https://support.google.com/a/answer/1371415?hl=es)
#### IBM i 7.3 - Regular Expressions
🔗[IBM Documentation](https://www.ibm.com/docs/es/i/7.3?topic=expressions-regular)
#### Graphviz - Graph Visualization Software
🔗[Graphviz Documentation](https://graphviz.org/)
#### Regular Expressions - MDN Web Docs
🔗[Mozilla Developer Network (MDN)]( https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_expressions)

## ⚖️ Licencia
📌 UVG License
Este proyecto es de código abierto bajo la licencia UVG. Puedes usarlo, modificarlo y distribuirlo libremente.
