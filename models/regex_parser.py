import re
from collections import deque

class RegexParser:
    OPERATORS = {'|', '.', '*'}  # Operadores reconocidos
    PRECEDENCE = {'|': 1, '.': 2, '*': 3}  # Prioridad de operadores

    def __init__(self, regex):
        self.regex = regex
        self.tokens = []
    
    def tokenize(self):
        """
        Convierte la expresión regular en una lista de tokens, insertando concatenaciones explícitas.
        """
        output = []
        prev = None  # Último carácter procesado
        for char in self.regex:
            if char.isalnum() or char == '#':  # Símbolo o marcador de fin
                if prev and (prev.isalnum() or prev == '*' or prev == ')'):
                    output.append('.')  # Agrega la concatenación implícita
                output.append(char)
            elif char in self.OPERATORS:
                output.append(char)
            elif char == '(':
                if prev and (prev.isalnum() or prev == '*' or prev == ')'):
                    output.append('.')  # Concatenación implícita antes del paréntesis
                output.append(char)
            elif char == ')':
                output.append(char)
            prev = char
        self.tokens = output
        return output
    
    def to_postfix(self):
        """
        Convierte la expresión regular en notación postfija (RPN) usando el algoritmo de Shunting-yard.
        """
        output = []
        stack = deque()
        
        for token in self.tokens:
            if token.isalnum() or token == '#':  # Si es un símbolo, agrégalo a la salida
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # Elimina el '('
            elif token in self.OPERATORS:
                while (stack and stack[-1] in self.OPERATORS and
                       self.PRECEDENCE[token] <= self.PRECEDENCE[stack[-1]]):
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
    regex = "(a|b)*abb#"
    parser = RegexParser(regex)
    postfix = parser.parse()
    print("Tokens:", parser.tokens)
    print("Postfix:", postfix)

    #caracter de escape
    