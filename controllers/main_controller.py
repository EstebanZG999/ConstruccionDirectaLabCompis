# main_controller.py
from models.dfa import build_dfa
from views.cli_view import get_user_input, show_dfa_construction_info, show_result
# Asumiendo que la persona A expone un método parse_regex que retorne la raíz del árbol
from models.regex_parser import parse_regex  

def run():
    # 1. Obtener inputs
    regex, cadena = get_user_input()

    # 2. Parsear la expresión regular y construir el árbol
    syntax_tree = parse_regex(regex)  # <-- Persona A

    # 3. Construir el AFD
    dfa = build_dfa(syntax_tree)

    # (Opcional) Mostrar información sobre el AFD
    show_dfa_construction_info(dfa)

    # 4. Simular la cadena
    is_accepted = dfa.simulate(cadena)

    # 5. Mostrar resultado
    show_result(is_accepted)
