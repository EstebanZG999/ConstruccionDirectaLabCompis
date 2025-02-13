# models/dfa.py
import graphviz
from models.syntax_tree import NodoHoja, NodoBinario, NodoUnario, SyntaxTree

class DFA:
    def __init__(self, syntax_tree):
        self.syntax_tree = syntax_tree
        # Calcula la función followpos y el mapeo de posiciones a símbolos
        self.followpos = self.compute_followpos(syntax_tree.raiz)
        self.pos_to_symbol = self.compute_pos_to_symbol(syntax_tree.raiz)
        # Definir el alfabeto (excluimos el marcador '#' de entrada)
        self.alphabet = {symbol for pos, symbol in self.pos_to_symbol.items() if symbol != '#'}
        # Diccionario para almacenar los estados (clave: frozenset de posiciones, valor: ID del estado)
        self.states = {}
        # Tabla de transiciones: {estado_id: {símbolo: estado_id_destino}}
        self.transitions = {}
        self.initial_state = None
        self.accepting_states = set()
        # Construir el AFD
        self.build_dfa()

    def compute_followpos(self, node):
        followpos = {}

        def init_followpos(n):
            if isinstance(n, NodoHoja):
                followpos[n.posicion] = set()
            elif isinstance(n, NodoBinario):
                init_followpos(n.izquierdo)
                init_followpos(n.derecho)
            elif isinstance(n, NodoUnario):
                init_followpos(n.hijo)
        init_followpos(node)

        def traverse(n):
            if isinstance(n, NodoBinario):
                traverse(n.izquierdo)
                traverse(n.derecho)
                if n.valor == '.':
                    # Para cada p en lastpos(izquierdo), followpos[p] += firstpos(derecho)
                    for pos in n.izquierdo.lastpos:
                        followpos[pos].update(n.derecho.firstpos)
            elif isinstance(n, NodoUnario):
                traverse(n.hijo)
                if n.valor == '*':
                    # Para cada p en lastpos(hijo), followpos[p] += firstpos(hijo)
                    for pos in n.hijo.lastpos:
                        followpos[pos].update(n.hijo.firstpos)
            # NodoHoja no hace nada
        traverse(node)

        return followpos


    def compute_pos_to_symbol(self, node):
        """Crea un diccionario que mapea cada posición de un nodo hoja a su símbolo."""
        pos_to_symbol = {}

        def traverse(n):
            if isinstance(n, NodoHoja):
                pos_to_symbol[n.posicion] = n.valor
            elif isinstance(n, NodoBinario):
                traverse(n.izquierdo)
                traverse(n.derecho)
            elif isinstance(n, NodoUnario):
                traverse(n.hijo)
        traverse(node)
        return pos_to_symbol

    def build_dfa(self):
        initial = frozenset(self.syntax_tree.raiz.firstpos)
        self.states[initial] = 0
        self.initial_state = 0
        unmarked_states = [initial]
        state_id_counter = 0

        while unmarked_states:
            current = unmarked_states.pop(0)
            current_state_id = self.states[current]
            self.transitions[current_state_id] = {}

            for symbol in self.alphabet:
                u = set()
                for pos in current:
                    if self.pos_to_symbol[pos] == symbol:
                        u.update(self.followpos[pos])
                if u:
                    u = frozenset(u)
                    if u not in self.states:
                        state_id_counter += 1
                        self.states[u] = state_id_counter
                        unmarked_states.append(u)
                    self.transitions[current_state_id][symbol] = self.states[u]

        # Estados de aceptación
        for state_set, state_id in self.states.items():
            if any(self.pos_to_symbol[pos] == '#' for pos in state_set):
                self.accepting_states.add(state_id)


    def simulate(self, string):
        """Simula el AFD con la cadena de entrada 'string'. Devuelve True si se acepta, False en caso contrario."""
        current_state = self.initial_state
        for ch in string:
            # Si no existe una transición para el símbolo, se rechaza la cadena.
            if ch in self.transitions[current_state]:
                current_state = self.transitions[current_state][ch]
            else:
                return False
        return current_state in self.accepting_states

    def print_dfa(self):
        """Imprime la tabla de transiciones y los estados de aceptación."""
        print("Estados y sus conjuntos de posiciones:")
        for state_set, state_id in self.states.items():
            aceptacion = " (aceptación)" if state_id in self.accepting_states else ""
            print(f"Estado {state_id}{aceptacion}: {set(state_set)}")
        print("\nTransiciones:")
        for state_id, trans in self.transitions.items():
            for symbol, target in trans.items():
                print(f"  δ({state_id}, '{symbol}') = {target}")



    def render_dfa(self, filename="dfa"):
        """
        Genera un diagrama del AFD usando Graphviz.
        Cada estado se representa por su ID y (opcionalmente) su conjunto de posiciones.
        """
        dot = graphviz.Digraph(format="png")

        # Agregar estados
        for state_set, state_id in self.states.items():
            # Marca los estados de aceptación con doble círculo
            shape = "doublecircle" if state_id in self.accepting_states else "circle"
            # Etiqueta: muestra state_id y (si deseas) las posiciones
            label = f"q{state_id}\n{state_set}"  
            dot.node(str(state_id), label=label, shape=shape)

        # Estado inicial: dibujar una flecha vacía que apunta al estado inicial
        dot.node("start", shape="none", label="")
        dot.edge("start", str(self.initial_state))

        # Agregar transiciones
        for state_id, trans_dict in self.transitions.items():
            for symbol, target_id in trans_dict.items():
                dot.edge(str(state_id), str(target_id), label=symbol)

        # Renderizar
        dot.render(filename, view=True)

 
 
if __name__ == "__main__":
    # Ejemplo de uso:
    # 1. Se define una expresión regular.
    regex = "(a|b)*abb#"
    # 2. Se crea el parser y se genera la notación postfija.
    from regex_parser import RegexParser
    parser = RegexParser(regex)
    postfix = parser.parse()
    # 3. Se construye el árbol sintáctico.
    syntax_tree = SyntaxTree(postfix)
    # 4. Se construye el AFD a partir del árbol sintáctico.
    dfa = DFA(syntax_tree)
    
    # Imprime la tabla de transiciones y los estados.
    print("Tokens:", [str(token) for token in parser.tokens])
    print("Postfix:", [str(token) for token in postfix])

    dfa.print_dfa()
    
    # 5. Simulación del AFD con cadenas de prueba.
    test_strings = ["aaabb", "aabb", "ababb", "ababbbbabb"]
    for s in test_strings:
        result = dfa.simulate(s)
        print(f"\nLa cadena '{s}' {'es aceptada' if result else 'NO es aceptada'} por la expresión regular.")

    dfa.render_dfa("dfa")  