# dfa.py

from syntax_tree import NodoHoja, NodoBinario, NodoUnario, SyntaxTree

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
        """Calcula la función followpos para cada posición del árbol."""
        followpos = {}

        # Primero, inicializamos followpos para cada hoja (NodoHoja)
        def init_followpos(n):
            if isinstance(n, NodoHoja):
                followpos[n.posicion] = set()
            elif isinstance(n, NodoBinario):
                init_followpos(n.izquierdo)
                init_followpos(n.derecho)
            elif isinstance(n, NodoUnario):
                init_followpos(n.hijo)
        init_followpos(node)

        # Ahora, recorremos el árbol para actualizar followpos según el operador
        def traverse(n):
            if isinstance(n, NodoBinario):
                traverse(n.izquierdo)
                traverse(n.derecho)
                if n.valor == '.':
                    # Para cada posición en lastpos del hijo izquierdo, se añade firstpos del hijo derecho.
                    for pos in n.izquierdo.lastpos:
                        followpos[pos] = followpos[pos].union(n.derecho.firstpos)
            elif isinstance(n, NodoUnario):
                traverse(n.hijo)
                if n.valor == '*':
                    # Para cada posición en lastpos del hijo, se añade firstpos del mismo hijo.
                    for pos in n.hijo.lastpos:
                        followpos[pos] = followpos[pos].union(n.hijo.firstpos)
            # Para NodoHoja no se hace nada
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
        """Construye el AFD utilizando la función followpos y la notación de conjuntos de posiciones."""
        # Estado inicial: firstpos de la raíz del árbol
        initial = frozenset(self.syntax_tree.raiz.firstpos)
        self.states[initial] = 0  # Asignamos el ID 0 al estado inicial
        self.initial_state = 0
        unmarked_states = [initial]
        state_id_counter = 0

        # Algoritmo de construcción
        while unmarked_states:
            current = unmarked_states.pop(0)
            current_state_id = self.states[current]
            self.transitions[current_state_id] = {}

            for symbol in self.alphabet:
                # Para cada símbolo, calculamos el conjunto U:
                # U = ⋃ { followpos(p) | p ∈ current y el símbolo en p es 'symbol' }
                u = set()
                for pos in current:
                    if self.pos_to_symbol[pos] == symbol:
                        u = u.union(self.followpos[pos])
                if u:
                    u = frozenset(u)
                    if u not in self.states:
                        state_id_counter += 1
                        self.states[u] = state_id_counter
                        unmarked_states.append(u)
                    self.transitions[current_state_id][symbol] = self.states[u]

        # Definir los estados de aceptación: aquellos estados que contienen la posición del marcador '#'
        for state_set, state_id in self.states.items():
            for pos in state_set:
                if self.pos_to_symbol[pos] == '#':
                    self.accepting_states.add(state_id)
                    break

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
    test_strings = ["abab", "aabb", "ababb", "ababbbbabb"]
    for s in test_strings:
        result = dfa.simulate(s)
        print(f"\nLa cadena '{s}' {'es aceptada' if result else 'NO es aceptada'} por la expresión regular.")
