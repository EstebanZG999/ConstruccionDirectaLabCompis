import re
from collections import deque

class Symbol:
    def __init__(self, value, is_operator=False):
        self.value = value
        self.is_operator = is_operator

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value 

class RegexParser:
    OPERATORS = {'|', '.', '*', '+'} 
    PRECEDENCE = {'|': 1, '.': 2, '*': 3, '+': 3} 

    def __init__(self, regex):
        self.regex = regex
        self.tokens = []
    
    def should_concat(self, last_token, current_token_type):
        """
        Decide si se debe insertar un operador de concatenación antes de agregar un token
        """
        if last_token is None:
            return False
        if last_token.is_operator:
            if last_token.value not in {')', '*'}:
                return False
        # Si el token actual es literal o el inicio de un grupo, se concatena.
        if current_token_type in ['literal', 'group_start']:
            return True
        return False
    
    def tokenize(self):
        """
        Convierte la expresión regular en una lista de tokens, insertando concatenaciones explícitas.
        Se utiliza enumerate para saber cuándo es el último carácter (por ejemplo, para el '#' final).
        """
        output = []
        last_token = None 
        escaped = False
        
        for i, char in enumerate(self.regex):
            if escaped: # Si el carácter está escapado, lo tratamos como literal.
                if self.should_concat(last_token, 'literal'):
                    output.append(Symbol('.', is_operator=True))
                token = Symbol(char, is_operator=False)
                output.append(token)
                last_token = token
                escaped = False
                continue
            elif char == '\\':
                escaped = True
                continue
            elif char.isalnum() or char == '#':  # Simbolo o marcador de fin
                # Inserta concatenación si no es el último
                if not (char == '#' and i == len(self.regex) - 1):
                    if self.should_concat(last_token, 'literal'):
                        output.append(Symbol('.', is_operator=True))
                token = Symbol(char, is_operator=False)
                output.append(token)
                last_token = token
                continue
            elif char == '+': # Sólo se aplica si NO está escapado 
                if last_token is None:
                    raise ValueError("El operador '+' no tiene un operando válido.")
                output.append(Symbol('.', is_operator=True))
                token_literal = Symbol(last_token.value, is_operator=False)
                output.append(token_literal)
                token_kleene = Symbol('*', is_operator=True)
                output.append(token_kleene)
                last_token = token_kleene
                continue
            elif char in self.OPERATORS:
                token = Symbol(char, is_operator=True)
                output.append(token)
                if char == '|':
                    last_token = None
                else:
                    last_token = token
                continue
            elif char == '(':
                if self.should_concat(last_token, 'group_start'):
                    output.append(Symbol('.', is_operator=True))
                token = Symbol('(', is_operator=True)
                output.append(token)
                last_token = None
                continue
            elif char == ')':
                token = Symbol(')', is_operator=True)
                output.append(token)
                last_token = token
                continue
            raise ValueError(f"Carácter no reconocido: {char}")

        if escaped:
            raise ValueError("Secuencia de escape incompleta en la expresión regular.")

        self.tokens = output
        return output
    
    def to_postfix(self):
        """
        Convierte la expresión regular (con concatenaciones explícitas) en notación postfija (RPN)
        usando una variante del algoritmo de Shunting-yard.
        Además, al vaciar la pila se descarta el operador de concatenación si se aplicaría a '#' final.
        """
        output = []
        stack = deque()
        
        for token in self.tokens:
            if not token.is_operator:
                output.append(token)
            elif token.value == '(':
                stack.append(token)
            elif token.value == ')':
                while stack and stack[-1].value != '(':
                    output.append(stack.pop())
                stack.pop()  # Descarta el '('
            elif token.value in {'|', '.'}:  # operadores binarios
                while (stack and stack[-1].value in {'|', '.'} and
                       self.PRECEDENCE[token.value] <= self.PRECEDENCE[stack[-1].value]):
                    output.append(stack.pop())
                stack.append(token)
            elif token.value == '*':  # operador unario (postfijo): se coloca directamente en la salida
                output.append(token)
            else:
                stack.append(token)
        
        while stack:
            op = stack.pop()
            if op.value == '.' and output and output[-1].value == '#':
                continue
            output.append(op)

        return output
    
    def parse(self):
        """
        Método principal que convierte la expresión en tokens y en notación postfija.
        """
        self.tokenize()
        return self.to_postfix()

if __name__ == "__main__":
    regex = r"(a|b)*a+bb#"
    parser = RegexParser(regex)
    postfix = parser.parse()
    print("Tokens:", [str(token) for token in parser.tokens])  
    print("Postfix:", [str(token) for token in postfix])  
