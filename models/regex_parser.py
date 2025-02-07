import re
from collections import deque

class Symbol:
    def __init__(self, value, is_operator=False):
        self.value = value
        self.is_operator = is_operator

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"Symbol({self.value}, is_operator={self.is_operator})"

class RegexParser:
    OPERATORS = {'|', '.', '*', '+'}  # Operadores reconocidos
    PRECEDENCE = {'|': 1, '.': 2, '*': 3, '+': 3}  # Prioridad de operadores
    
    def __init__(self, regex):
        self.regex = regex
        self.tokens = []
    
    def tokenize(self):
        """
        Convierte la expresión regular en una lista de tokens, insertando concatenaciones explícitas.
        """
        output = []
        prev = None  # Último carácter procesado
        escaped = False
        
        for char in self.regex:
            if escaped:
                output.append(Symbol(char))
                escaped = False
            elif char == '\\':
                escaped = True
            elif char.isalnum() or char == '#':  # Símbolo o marcador de fin
                if prev and (isinstance(prev, Symbol) and not prev.is_operator or prev.value in {'*', '+', ')'}):
                    output.append(Symbol('.'))  # Agrega la concatenación implícita
                output.append(Symbol(char))
            elif char in self.OPERATORS:
                output.append(Symbol(char, is_operator=True))
            elif char == '(':
                if prev and (isinstance(prev, Symbol) and not prev.is_operator or prev.value in {'*', '+', ')'}):
                    output.append(Symbol('.'))  # Concatenación implícita antes del paréntesis
                output.append(Symbol(char, is_operator=True))
            elif char == ')':
                output.append(Symbol(char, is_operator=True))
            prev = output[-1] if output else None
        
        self.tokens = output
        return output
    
    def to_postfix(self):
        """
        Convierte la expresión regular en notación postfija (RPN) usando el algoritmo de Shunting-yard.
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
                stack.pop()
            elif token.value in self.OPERATORS:
                while (stack and stack[-1].value in self.OPERATORS and
                       self.PRECEDENCE[token.value] <= self.PRECEDENCE[stack[-1].value]):
                    output.append(stack.pop())
                stack.append(token)
        
        while stack:
            output.append(stack.pop())
        
        return output
    
    def parse(self):
        """
        Método principal que convierte la expresión en tokens y en notación postfija.
        """
        self.tokenize()
        return self.to_postfix()

if __name__ == "__main__":
    regex = "(a|b)+a*bb#"
    parser = RegexParser(regex)
    postfix = parser.parse()
    print("Tokens:", [str(token) for token in parser.tokens])
    print("Postfix:", [str(token) for token in postfix])