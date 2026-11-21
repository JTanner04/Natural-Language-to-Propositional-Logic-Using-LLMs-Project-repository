"""Safe tokenizer and recursive-descent parser for propositional logic."""
from __future__ import annotations

from dataclasses import dataclass
import re


class FormulaError(ValueError):
    """Raised when a formula is malformed or uses an unknown symbol."""


@dataclass(frozen=True)
class Node:
    op: str
    value: str | None = None
    left: "Node | None" = None
    right: "Node | None" = None


TOKEN_RE = re.compile(r"\s*(<->|<=>|->|=>|\(|\)|¬|∧|∨|→|↔|!|~|&|\||[A-Za-z][A-Za-z0-9_]*)")
ALIASES = {"!": "NOT", "~": "NOT", "¬": "NOT", "&": "AND", "∧": "AND",
           "|": "OR", "∨": "OR", "->": "IMPLIES", "=>": "IMPLIES", "→": "IMPLIES",
           "<->": "IFF", "<=>": "IFF", "↔": "IFF"}
WORDS = {"NOT": "NOT", "AND": "AND", "OR": "OR", "IMPLIES": "IMPLIES", "IFF": "IFF"}


def tokenize(text: str) -> list[str]:
    tokens, position = [], 0
    while position < len(text):
        match = TOKEN_RE.match(text, position)
        if not match:
            if text[position:].strip() == "":
                break
            raise FormulaError(f"Unexpected character at position {position}: {text[position]!r}")
        token = match.group(1)
        tokens.append(ALIASES.get(token, WORDS.get(token.upper(), token)))
        position = match.end()
    if not tokens:
        raise FormulaError("Formula is empty")
    return tokens


class _Parser:
    def __init__(self, tokens: list[str], allowed: set[str] | None):
        self.tokens, self.allowed, self.i = tokens, allowed, 0

    def peek(self): return self.tokens[self.i] if self.i < len(self.tokens) else None
    def take(self):
        token = self.peek()
        if token is None: raise FormulaError("Unexpected end of formula")
        self.i += 1
        return token

    # Lowest to highest binding: iff, implication (right associative), or, and, not.
    def parse(self) -> Node:
        node = self.iff()
        if self.peek() is not None: raise FormulaError(f"Unexpected token: {self.peek()}")
        return node
    def iff(self) -> Node:
        node = self.implies()
        while self.peek() == "IFF": node = Node("IFF", left=node, right=(self.take() and self.implies()))
        return node
    def implies(self) -> Node:
        node = self.or_expr()
        if self.peek() == "IMPLIES": self.take(); node = Node("IMPLIES", left=node, right=self.implies())
        return node
    def or_expr(self) -> Node:
        node = self.and_expr()
        while self.peek() == "OR": self.take(); node = Node("OR", left=node, right=self.and_expr())
        return node
    def and_expr(self) -> Node:
        node = self.unary()
        while self.peek() == "AND": self.take(); node = Node("AND", left=node, right=self.unary())
        return node
    def unary(self) -> Node:
        if self.peek() == "NOT": self.take(); return Node("NOT", left=self.unary())
        if self.peek() == "(":
            self.take(); node = self.iff()
            if self.take() != ")": raise FormulaError("Expected closing parenthesis")
            return node
        token = self.take()
        if token in {"AND", "OR", "IMPLIES", "IFF", ")", "("}: raise FormulaError(f"Expected proposition, got {token}")
        if self.allowed is not None and token not in self.allowed: raise FormulaError(f"Unknown proposition: {token}")
        return Node("VAR", value=token)


def parse_formula(text: str, allowed_symbols: set[str] | None = None) -> Node:
    return _Parser(tokenize(text), allowed_symbols).parse()


def variables(node: Node) -> set[str]:
    if node.op == "VAR": return {node.value}  # type: ignore[return-value]
    return variables(node.left) | (variables(node.right) if node.right else set())  # type: ignore[arg-type]


DISPLAY = {"NOT": "¬", "AND": "∧", "OR": "∨", "IMPLIES": "→", "IFF": "↔"}
def to_display(node: Node) -> str:
    if node.op == "VAR": return node.value or ""
    if node.op == "NOT": return f"¬{to_display(node.left)}"  # type: ignore[arg-type]
    return f"({to_display(node.left)} {DISPLAY[node.op]} {to_display(node.right)})"  # type: ignore[arg-type]
