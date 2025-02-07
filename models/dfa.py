# dfa.py
from typing import Set, Dict, List, Optional

class DFA:
    """
    Clase para representar y simular un AFD construido
    mediante el algoritmo directo (posiciones).
    """
    def __init__(self, transitions: Dict[frozenset, Dict[str, frozenset]],
                 initial_state: frozenset,
                 accept_states: List[frozenset]):
        """
        :param transitions: Mapa de estado -> (símbolo -> estado siguiente)
                            donde estado es un frozenset de posiciones.
        :param initial_state: Conjunto (inmutable) de posiciones que representan el estado inicial.
        :param accept_states: Lista de estados finales.
        """
        self.transitions = transitions
        self.initial_state = initial_state
        self.accept_states = accept_states

    def simulate(self, input_string: str) -> bool:
        """
        Determina si la cadena de entrada es aceptada por este AFD.
        :param input_string: Cadena a evaluar.
        :return: True si es aceptada, False en caso contrario.
        """
        current_state = self.initial_state

        for symbol in input_string:
            # Si no existe transición para el símbolo, la cadena se rechaza
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return False
            current_state = self.transitions[current_state][symbol]

        # Verificar si el estado final es de aceptación
        return current_state in self.accept_states


def build_dfa(syntax_tree) -> DFA:
    """
    Construye el AFD a partir de un árbol sintáctico que ya tiene calculados
    nullable, firstpos, lastpos y un número de posición en cada hoja.
    Se asume que la posición del símbolo '#' es la última o está bien identificada.

    :param syntax_tree: Raíz del árbol sintáctico anotado.
    :return: Instancia de la clase DFA construida.
    """

    # 1. Recolectar información de las hojas
    # Aquí necesitarás una función que recorra el árbol y recopile:
    #   - La posición asociada a cada nodo hoja.
    #   - El símbolo que contiene.
    #   - La posición especial del símbolo #.
    #
    # Persona A debe proveer un método para obtener esto, o podrías implementarlo
    #   de manera que al recorrer el árbol, armes una lista o diccionario.
    #
    # Por ejemplo:
    # leaves_info = collect_leaves_info(syntax_tree)  # Suponiendo que sea un dict: {pos -> symbol}
    leaves_info = _collect_leaves_info(syntax_tree)

    # 2. Calcular followpos para cada posición
    # Lo normal es que en tu árbol ya hayas guardado un diccionario "followpos[pos] = { ... }"
    # durante la anotación. Pero si aún no está calculado, aquí lo harías.
    # Por ejemplo:
    # followpos_map = compute_followpos(syntax_tree)
    followpos_map = _compute_followpos(syntax_tree)

    # Identificar la posición correspondiente a '#'
    end_position = None
    for pos, symbol in leaves_info.items():
        if symbol == '#':
            end_position = pos
            break

    # 3. Crear el estado inicial (firstpos de la raíz)
    initial_state = frozenset(syntax_tree.firstpos)  # Se asume que syntax_tree tiene un atributo firstpos

    # 4. Generar iterativamente todos los estados del AFD
    states_unmarked = [initial_state]
    dfa_states = [initial_state]  # lista (o set) de todos los estados encontrados
    transitions = {}
    accept_states = []

    while states_unmarked:
        current = states_unmarked.pop()
        transitions[current] = {}

        # Para cada símbolo posible que sale de current, calculamos el siguiente estado
        # Identificamos las posiciones en 'current' que tienen un símbolo particular
        # y unimos los followpos correspondientes.
        symbols_seen = {}  # símbolo -> set de followpos

        for pos in current:
            symbol = leaves_info[pos]
            if symbol != '#':  # No construimos transición con el marcador de fin
                if symbol not in symbols_seen:
                    symbols_seen[symbol] = set()
                symbols_seen[symbol].update(followpos_map[pos])

        # Ahora construimos las transiciones
        for symbol, nextpos_set in symbols_seen.items():
            next_state = frozenset(nextpos_set)
            transitions[current][symbol] = next_state

            if next_state not in dfa_states:
                dfa_states.append(next_state)
                states_unmarked.append(next_state)

    # 5. Determinar qué estados son finales
    # Un estado es final si contiene la posición del símbolo '#' en su conjunto
    for state in dfa_states:
        if end_position in state:
            accept_states.append(state)

    # 6. Instanciar y retornar el DFA
    return DFA(transitions=transitions,
               initial_state=initial_state,
               accept_states=accept_states)


# -----------------------------------------------------------------------------
# Funciones privadas / helpers (podrías moverlas a `utils/helpers.py`):
# -----------------------------------------------------------------------------

def _collect_leaves_info(syntax_tree) -> Dict[int, str]:
    """
    Recorre el árbol y devuelve un dict pos -> símbolo.
    Asume que cada hoja tiene atributos:
      - position: int (posición única en la expresión)
      - symbol: str (símbolo correspondiente, e.g. 'a', 'b', '#')
    """
    leaves = {}
    def _dfs(node):
        if node.is_leaf():
            leaves[node.position] = node.symbol
        else:
            for child in node.children:
                _dfs(child)

    _dfs(syntax_tree)
    return leaves


def _compute_followpos(syntax_tree) -> Dict[int, Set[int]]:
    """
    Computa el followpos de cada posición según las reglas:
      - Concatenación: lastpos(X) -> firstpos(Y)
      - Cerradura (*): lastpos(X*) -> firstpos(X*)
    Asume que el árbol ya tiene metadatos para:
      - node.firstpos
      - node.lastpos
      - node.nullable
    y que cada nodo interno sabe qué tipo de operación es.
    
    En muchos diseños, este diccionario se va llenando durante la construcción
    post-orden. Aquí lo mostramos simplificado como si lo hiciéramos
    en un solo recorrido.
    """
    # Inicializamos un mapa pos-> set()
    followpos_map = {}
    
    # Llenar con llaves vacías para todas las hojas
    def _init_followpos(node):
        if node.is_leaf():
            followpos_map[node.position] = set()
        else:
            for child in node.children:
                _init_followpos(child)
    _init_followpos(syntax_tree)

    # Recorremos el árbol en post-orden para aplicar las reglas
    def _postorder(node):
        # Procesar hijos primero
        for child in getattr(node, 'children', []):
            _postorder(child)

        node_type = node.type  # 'CONCAT', 'UNION', 'KLEENE', o 'LEAF'
        if node_type == 'CONCAT':
            left, right = node.left, node.right
            for p in left.lastpos:
                followpos_map[p].update(right.firstpos)
        elif node_type == 'KLEENE':
            # lastpos(X*) se une con firstpos(X*)
            for p in node.lastpos:
                followpos_map[p].update(node.firstpos)
        # para la unión, no se hace nada especial
        # para las hojas, tampoco

    _postorder(syntax_tree)
    return followpos_map
