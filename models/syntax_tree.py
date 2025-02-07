import graphviz


class NodoBase:
    def __init__(self, valor):
        self.valor = valor
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()

class NodoHoja(NodoBase):
    def __init__(self, valor, posicion):
        super().__init__(valor)
        self.posicion = posicion
        self.firstpos.add(posicion)
        self.lastpos.add(posicion)
        self.nullable = False if valor != 'ε' else True


    def to_dot(self, graph):
        """ Agrega este nodo hoja al gráfico DOT. """
        graph.node(str(id(self)), f"{self.valor} ({self.posicion})", shape="ellipse")

class NodoBinario(NodoBase):
    def __init__(self, valor, izquierdo, derecho):
        super().__init__(valor)
        self.izquierdo = izquierdo
        self.derecho = derecho
        self.calcular_propiedades()

    def calcular_propiedades(self):
        if self.valor == '.':  # Concatenación
            self.nullable = self.izquierdo.nullable and self.derecho.nullable
            self.firstpos = self.izquierdo.firstpos | (self.derecho.firstpos if self.izquierdo.nullable else set())
            self.lastpos = self.derecho.lastpos | (self.izquierdo.lastpos if self.derecho.nullable else set())
        elif self.valor == '|':  # Alternancia
            self.nullable = self.izquierdo.nullable or self.derecho.nullable
            self.firstpos = self.izquierdo.firstpos | self.derecho.firstpos
            self.lastpos = self.izquierdo.lastpos | self.derecho.lastpos

    def to_dot(self, graph):
        """ Agrega este nodo binario y sus conexiones al gráfico DOT. """
        graph.node(str(id(self)), self.valor, shape="box")
        self.izquierdo.to_dot(graph)
        self.derecho.to_dot(graph)
        graph.edge(str(id(self)), str(id(self.izquierdo)))
        graph.edge(str(id(self)), str(id(self.derecho)))

class NodoUnario(NodoBase):
    def __init__(self, valor, hijo):
        super().__init__(valor)
        self.hijo = hijo
        self.calcular_propiedades()

    def calcular_propiedades(self):
        if self.valor == '*':  # Cerradura de Kleene
            self.nullable = True
            self.firstpos = self.hijo.firstpos
            self.lastpos = self.hijo.lastpos

    def to_dot(self, graph):
        """ Agrega este nodo unario y su conexión al gráfico DOT. """
        graph.node(str(id(self)), self.valor, shape="diamond")
        self.hijo.to_dot(graph)
        graph.edge(str(id(self)), str(id(self.hijo)))

class SyntaxTree:
    def __init__(self, postfix):
        self.postfix = postfix
        self.posicion_actual = 1
        self.raiz = self.construir_arbol()
    
    def construir_arbol(self):
        stack = []
        for token in self.postfix:
            if token.isalnum() or token == '#':  # Nodo hoja
                stack.append(NodoHoja(token, self.posicion_actual))
                self.posicion_actual += 1
            elif token == '*':  # Nodo unario
                nodo = stack.pop()
                stack.append(NodoUnario(token, nodo))
            elif token in {'.', '|'}:  # Nodo binario
                derecho = stack.pop()
                izquierdo = stack.pop()
                stack.append(NodoBinario(token, izquierdo, derecho))
        return stack.pop()
    
    def obtener_raiz(self):
        return self.raiz
    
    def render(self, filename="syntax_tree"):
        """Genera una imagen del árbol sintáctico usando Graphviz."""
        dot = graphviz.Digraph(format="png")
        if self.raiz:
            self.raiz.to_dot(dot)
        dot.render(filename, view=True)  # Renderiza y abre la imagen

if __name__ == "__main__":
    from regex_parser import RegexParser
    regex = "(a|b)*abb#"
    parser = RegexParser(regex)
    postfix = parser.parse()
    
    syntax_tree = SyntaxTree(postfix)
    raiz = syntax_tree.obtener_raiz()
    
    print("Árbol sintáctico construido correctamente.")