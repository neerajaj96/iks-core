"""IKS-NN expression parser (stdlib, no deps).

Covers the intensional-logic fragment; everything else parses as Opaque
(never raises on corpus input — residue, not error).
  Limiters:    A_phi(x)
  Roles:       PR_{phi,R}(x)  AN_R(y)
  Absences:    ¬_p ¬_d ¬_a  and  x ≠_id y
  Pervasion:   H ⇉ S   H ⇉[limiter] S
  Occurrence:  x ⊏_R y
  Predication: P(a)   Quantification: ∀x(...)   Conclusion: ∴ P(a)
  Validators:  V_An=0 via Y   V_Sa iff ...
  Modals/sets: ◇_n   y ⊆_sakti Prakrti
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field

OPS = ["≠_id", "¬_p", "¬_d", "¬_a", "⇉", "⊏", "∴", "∀", "⊆", "∧", "→", "="]
_OPCHARS = "¬⇉⊏∴∀⊆∧→≠="


@dataclass
class Node:
    kind: str
    text: str = ""
    children: list = field(default_factory=list)
    attrs: dict = field(default_factory=dict)

    def __repr__(self):  # compact
        if self.kind == "Func":
            return f"{self.text}({', '.join(map(repr, self.children))})"
        if self.children:
            return f"{self.kind}({', '.join(map(repr, self.children))})"
        return f"{self.kind}[{self.text}]" if self.text else self.kind


class ParseError(Exception):
    pass


def tokenize(s: str) -> list[str]:
    toks, i = [], 0
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        hit = next((op for op in OPS if s.startswith(op, i)), None)
        if hit:
            toks.append(hit)
            i += len(hit)
            continue
        if s[i] in "(),;[]{}&":
            toks.append(s[i])
            i += 1
            continue
        m = re.match(r"[^\s(),;\(\)\[\]{}&¬⇉⊏∴∀⊆∧→≠=]+", s[i:])
        if not m:  # lone operator char (e.g. bare ¬): keep as opaque token
            toks.append(s[i])
            i += 1
            continue
        toks.append(m.group(0))
        i += m.end()
    return toks


class Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else ""

    def next(self):
        tok = self.peek()
        self.i += 1
        return tok

    def parse(self) -> Node:
        parts = [self.seq()]
        while self.peek() == ";":
            self.next()
            if self.peek():
                parts.append(self.seq())
        node = parts[0] if len(parts) == 1 else Node("Seq", children=parts)
        if self.i < len(self.t):  # trailing residue kept explicitly, never dropped
            node = Node("Seq", children=[node, Node("Opaque", " ".join(self.t[self.i:]))])
        return node

    def seq(self) -> Node:
        parts = [self.conj()]
        while self.peek() in ("∧", "&", ","):
            self.next()
            parts.append(self.conj())
        return parts[0] if len(parts) == 1 else Node("And", children=parts)

    def conj(self) -> Node:
        tok = self.peek()
        if tok in ("¬_p", "¬_d", "¬_a"):
            self.next()
            return Node("Absence", tok, [self.atom()])
        if tok == "∀":
            self.next()
            var = self.next()
            return Node("Forall", var, [self.atom() if self.peek() != "(" else self.paren()])
        if tok == "∴":
            self.next()
            return Node("Therefore", children=[self.seq()])
        return self.binary()

    def paren(self) -> Node:
        assert self.next() == "("
        n = self.seq()
        if self.peek() == ")":
            self.next()
        return n

    def atom(self) -> Node:
        tok = self.peek()
        if tok == "(":
            return self.paren()
        if not tok:
            raise ParseError("empty")
        self.next()
        if self.peek() == "(":
            self.next()
            args = []
            if self.peek() != ")":
                args.append(self.seq())
                while self.peek() == ",":
                    self.next()
                    args.append(self.seq())
            if self.peek() == ")":
                self.next()
            return Node("Func", tok, args)
        return Node("Term", tok)

    def binary(self) -> Node:
        left = self.atom()
        tok = self.peek()
        if tok in ("⇉", "⊆", "≠_id", "⊏", "→", "="):
            self.next()
            if tok == "⇉" and self.peek() == "[":
                self.next()
                lim = []
                if self.peek() != "]":
                    lim.append(self.seq())
                if self.peek() == "]":
                    self.next()
                right = self.binary()
                return Node("Vyapti", children=[left, right], attrs={"limiter": lim})
            if tok == "⊆" and self.peek().startswith("_"):
                rel = self.next()  # subscript relation marker, e.g. _sakti
                right = self.binary()
                return Node("Subset", children=[left, right], attrs={"rel": rel})
            right = self.atom()
            names = {"⇉": "Vyapti", "⊆": "Subset", "≠_id": "MutualAbsence",
                     "⊏": "Occurs", "→": "Implies", "=": "Eq"}
            return Node(names[tok], children=[left, right])
        return left


def parse(s: str) -> Node:
    """Parse never raises: unparsable input becomes Opaque."""
    try:
        toks = tokenize(s)
        if not toks:
            return Node("Opaque", s)
        return Parser(toks).parse()
    except (ParseError, AssertionError, IndexError, RecursionError):
        return Node("Opaque", s)


def is_logic(node: Node) -> bool:
    return node.kind != "Opaque"


def walk(node: Node):
    yield node
    for c in node.children:
        yield from walk(c)
