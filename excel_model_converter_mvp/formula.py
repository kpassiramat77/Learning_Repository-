from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .models import ExpressionNode


@dataclass
class Token:
    token_type: str
    value: str


OPERATORS = {
    ">=",
    "<=",
    "<>",
    ">",
    "<",
    "=",
    "+",
    "-",
    "*",
    "/",
    "^",
    "&",
}


def tokenize(expression: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    while i < len(expression):
        char = expression[i]
        if char.isspace():
            i += 1
            continue
        if char in "(),:":
            tokens.append(Token(char, char))
            i += 1
            continue
        if char in "<>=":
            if i + 1 < len(expression) and expression[i : i + 2] in OPERATORS:
                tokens.append(Token("OP", expression[i : i + 2]))
                i += 2
                continue
            tokens.append(Token("OP", char))
            i += 1
            continue
        if char in "+-*/^&":
            tokens.append(Token("OP", char))
            i += 1
            continue
        if char == '"':
            end = i + 1
            while end < len(expression) and expression[end] != '"':
                end += 1
            tokens.append(Token("STRING", expression[i + 1 : end]))
            i = end + 1
            continue
        if char.isdigit() or (char == "." and i + 1 < len(expression) and expression[i + 1].isdigit()):
            end = i + 1
            while end < len(expression) and (expression[end].isdigit() or expression[end] == "."):
                end += 1
            tokens.append(Token("NUMBER", expression[i:end]))
            i = end
            continue
        end = i + 1
        while end < len(expression) and re.match(r"[A-Za-z0-9_$!.]", expression[end]):
            end += 1
        tokens.append(Token("IDENT", expression[i:end]))
        i = end
    return tokens


class FormulaParser:
    def __init__(self, tokens: Iterable[Token]):
        self.tokens = list(tokens)
        self.position = 0

    def parse(self) -> ExpressionNode:
        if not self.tokens:
            return ExpressionNode(node_type="literal", value="")
        node = self.parse_comparison()
        return node

    def peek(self) -> Token | None:
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]

    def consume(self) -> Token:
        token = self.tokens[self.position]
        self.position += 1
        return token

    def parse_comparison(self) -> ExpressionNode:
        node = self.parse_term()
        while self.peek() and self.peek().token_type == "OP" and self.peek().value in {
            ">",
            "<",
            ">=",
            "<=",
            "=",
            "<>",
        }:
            op = self.consume().value
            right = self.parse_term()
            node = ExpressionNode(
                node_type="binary", operator=op, left=node, right=right
            )
        return node

    def parse_term(self) -> ExpressionNode:
        node = self.parse_factor()
        while self.peek() and self.peek().token_type == "OP" and self.peek().value in {
            "+",
            "-",
        }:
            op = self.consume().value
            right = self.parse_factor()
            node = ExpressionNode(
                node_type="binary", operator=op, left=node, right=right
            )
        return node

    def parse_factor(self) -> ExpressionNode:
        node = self.parse_power()
        while self.peek() and self.peek().token_type == "OP" and self.peek().value in {
            "*",
            "/",
        }:
            op = self.consume().value
            right = self.parse_power()
            node = ExpressionNode(
                node_type="binary", operator=op, left=node, right=right
            )
        return node

    def parse_power(self) -> ExpressionNode:
        node = self.parse_unary()
        while self.peek() and self.peek().token_type == "OP" and self.peek().value == "^":
            op = self.consume().value
            right = self.parse_unary()
            node = ExpressionNode(
                node_type="binary", operator=op, left=node, right=right
            )
        return node

    def parse_unary(self) -> ExpressionNode:
        token = self.peek()
        if token and token.token_type == "OP" and token.value in {"+", "-"}:
            op = self.consume().value
            operand = self.parse_unary()
            return ExpressionNode(
                node_type="unary", operator=op, operand=operand
            )
        return self.parse_primary()

    def parse_primary(self) -> ExpressionNode:
        token = self.peek()
        if token is None:
            return ExpressionNode(node_type="literal", value="")
        if token.token_type == "NUMBER":
            self.consume()
            if "." in token.value:
                return ExpressionNode(node_type="literal", value=float(token.value))
            return ExpressionNode(node_type="literal", value=int(token.value))
        if token.token_type == "STRING":
            self.consume()
            return ExpressionNode(node_type="literal", value=token.value)
        if token.token_type == "IDENT":
            self.consume()
            if token.value.upper() == "TRUE":
                return ExpressionNode(node_type="literal", value=True)
            if token.value.upper() == "FALSE":
                return ExpressionNode(node_type="literal", value=False)
            if self.peek() and self.peek().token_type == "(":
                self.consume()
                args = []
                while self.peek() and self.peek().token_type != ")":
                    args.append(self.parse_comparison())
                    if self.peek() and self.peek().token_type == ",":
                        self.consume()
                if self.peek() and self.peek().token_type == ")":
                    self.consume()
                return ExpressionNode(
                    node_type="function", name=token.value, args=args
                )
            ref_node = ExpressionNode(
                node_type="reference",
                ref=token.value,
                ref_type=_reference_type(token.value),
            )
            if self.peek() and self.peek().token_type == ":":
                self.consume()
                end_token = self.consume()
                if end_token.token_type == "IDENT":
                    return ExpressionNode(
                        node_type="range",
                        ref=f"{token.value}:{end_token.value}",
                        ref_type="cell",
                    )
            return ref_node
        if token.token_type == "(":
            self.consume()
            node = self.parse_comparison()
            if self.peek() and self.peek().token_type == ")":
                self.consume()
            return node
        self.consume()
        return ExpressionNode(node_type="literal", value=token.value)


def parse_formula_to_expression(formula: str) -> ExpressionNode:
    cleaned = formula[1:] if formula.startswith("=") else formula
    parser = FormulaParser(tokenize(cleaned))
    return parser.parse()


def extract_references(formula: str) -> list[str]:
    pattern = re.compile(r"(?:[A-Za-z_][A-Za-z0-9_]*!)?\$?[A-Za-z]{1,3}\$?\d+")
    references = sorted(set(match.group(0) for match in pattern.finditer(formula)))
    return references


def expression_to_string(node: ExpressionNode) -> str:
    if node.node_type == "literal":
        if isinstance(node.value, str):
            return f'"{node.value}"'
        if node.value is None:
            return ""
        return str(node.value)
    if node.node_type == "reference":
        return node.ref or ""
    if node.node_type == "range":
        return node.ref or ""
    if node.node_type == "unary":
        return f"{node.operator}{expression_to_string(node.operand)}"
    if node.node_type == "binary":
        left = expression_to_string(node.left)
        right = expression_to_string(node.right)
        return f"({left} {node.operator} {right})"
    if node.node_type == "function":
        args = ", ".join(expression_to_string(arg) for arg in (node.args or []))
        return f"{node.name}({args})"
    return ""


def _reference_type(value: str) -> str:
    if re.match(r"^(?:[A-Za-z_][A-Za-z0-9_]*!)?\$?[A-Za-z]{1,3}\$?\d+$", value):
        return "cell"
    return "name"
