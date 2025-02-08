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
    
    def tokenize(self):
        """
        Convierte la expresión regular en una lista de tokens, insertando concatenaciones explícitas.
        Se utiliza enumerate para saber cuándo es el último carácter (por ejemplo, para el '#' final).
        """
        output = []
        prev = None  
        escaped = False
        
        for i, char in enumerate(self.regex):
            if escaped:
                if prev and not prev.is_operator:
                    output.append(Symbol('.')) 
                output.append(Symbol(char, is_operator=False))
                escaped = False
            elif char == '\\':
                escaped = True
            elif char.isalnum() or char == '#':  # Simbolo o marcador de fin
                if not (char == '#' and i == len(self.regex) - 1):
                    if prev and (not prev.is_operator or prev.value in {'*', '+', ')'}):
                        output.append(Symbol('.'))
                output.append(Symbol(char, is_operator=False))
            elif char == '+':
                if prev and not prev.is_operator:  # Asegurar que + tiene un operando válido
                    output.append(Symbol('.'))  # Concatenación con sí mismo
                    output.append(Symbol(prev.value, is_operator=False)) # Se agrega el simbolo * nuevo
                    output.append(Symbol('*', is_operator=True))  # Se agrega la cerradura de Kleene
                else:
                    raise ValueError("El operador '+' no tiene un operando válido.")
            elif char in self.OPERATORS:
                output.append(Symbol(char, is_operator=True))
            elif char == '(':
                if prev and (not prev.is_operator or prev.value in {'*', '+', ')'}):
                    output.append(Symbol('.'))
                output.append(Symbol(char, is_operator=True))
            elif char == ')':
                output.append(Symbol(char, is_operator=True))
            prev = output[-1] if output else None

        if escaped:
            raise ValueError("Secuencia de escape incompleta en la expresión regular.")
        
        self.tokens = output
        return output
    
    def to_postfix(self):
        """
        Convierte la expresión regular (con concatenaciones explícitas) en notación postfija (RPN)
        usando una variante del algoritmo de Shunting-yard:
          - Los operadores binarios ('.' y '|') se manejan en la pila.
          - Los operadores unarios (como '*') se colocan directamente en la salida.
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
    regex = r"(a|b)\*a+bb#"
    parser = RegexParser(regex)
    postfix = parser.parse()
    print("Tokens:", [str(token) for token in parser.tokens])  
    print("Postfix:", [str(token) for token in postfix])  
