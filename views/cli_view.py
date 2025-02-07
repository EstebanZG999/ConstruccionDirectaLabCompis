# cli_view.py

from typing import Tuple

def get_user_input() -> Tuple[str, str]:
    """
    Solicita al usuario la expresión regular y la cadena por consola.
    Retorna una tupla (regex, cadena).
    """
    print("=== Bienvenido al Generador de AFD ===")
    regex = input("Ingresa la expresión regular: ")
    cadena = input("Ingresa la cadena a evaluar: ")
    return regex, cadena


def show_dfa_construction_info(dfa):
    """
    Muestra información sobre el AFD construido.
    Puede ser tan detallado como quieras: estados, transiciones, etc.
    """
    print("\n=== AFD Construido ===")
    print(f"Estado inicial: {dfa.initial_state}")
    print(f"Estados de aceptación: {dfa.accept_states}")

    print("\nTransiciones:")
    for state, transitions in dfa.transitions.items():
        for symbol, next_state in transitions.items():
            print(f"  δ({state}, '{symbol}') -> {next_state}")


def show_result(is_accepted: bool):
    """
    Muestra el resultado de la simulación de la cadena.
    :param is_accepted: True si la cadena es aceptada, False en caso contrario.
    """
    print("\n=== Resultado de la Simulación ===")
    if is_accepted:
        print("La cadena ha sido ACEPTADA por el AFD.")
    else:
        print("La cadena ha sido RECHAZADA por el AFD.")
