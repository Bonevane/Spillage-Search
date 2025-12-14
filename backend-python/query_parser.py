from abc import ABC, abstractmethod
from typing import List, Set, Optional
from dataclasses import dataclass

# 11: Recursive Data Types
# The Query structure is recursive: And(Query, Query), Or(Query, Query), etc.

class QueryNode(ABC):
    """
    Abstract base class for a query node in the AST.
    """
    @abstractmethod
    def __repr__(self) -> str:
        pass

@dataclass
class Term(QueryNode):
    word: str
    
    def __repr__(self) -> str:
        return f"Term('{self.word}')"

@dataclass
class And(QueryNode):
    left: QueryNode
    right: QueryNode
    
    def __repr__(self) -> str:
        return f"And({self.left}, {self.right})"

@dataclass
class Or(QueryNode):
    left: QueryNode
    right: QueryNode
    
    def __repr__(self) -> str:
        return f"Or({self.left}, {self.right})"

@dataclass
class Not(QueryNode):
    operand: QueryNode
    
    def __repr__(self) -> str:
        return f"Not({self.operand})"

# 12: Grammars & Parsing
# Grammar:
# Query -> OrTerm { 'OR' OrTerm }
# OrTerm -> AndTerm { 'AND' AndTerm }
# AndTerm -> 'NOT' Term | '(' Query ')' | Term
# Term -> word

class QueryParser:
    """
    A recursive descent parser for search queries.
    Supports AND, OR, NOT operators and parentheses.
    """
    def __init__(self, query_str: str):
        self.tokens = self._tokenize(query_str)
        self.pos = 0

    def _tokenize(self, query_str: str) -> List[str]:
        # Simple tokenizer: splits by space but keeps parentheses
        # This is a "Little Language" (19)
        raw_tokens = query_str.replace('(', ' ( ').replace(')', ' ) ').split()
        return [t for t in raw_tokens if t.strip()]

    def _peek(self) -> Optional[str]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self) -> str:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def parse(self) -> QueryNode:
        if not self.tokens:
            return Term("") # Empty query
        return self._parse_or()

    def _parse_or(self) -> QueryNode:
        left = self._parse_and()
        while self._peek() == 'OR':
            self._consume()
            right = self._parse_and()
            left = Or(left, right)
        return left

    def _parse_and(self) -> QueryNode:
        left = self._parse_unary()
        while self._peek() == 'AND':
            self._consume()
            right = self._parse_unary()
            left = And(left, right)
        # Implicit AND: "apple banana" -> "apple AND banana"
        while self._peek() and self._peek() not in (')', 'OR'):
            right = self._parse_unary()
            left = And(left, right)
        return left

    def _parse_unary(self) -> QueryNode:
        if self._peek() == 'NOT':
            self._consume()
            operand = self._parse_unary()
            return Not(operand)
        return self._parse_primary()

    def _parse_primary(self) -> QueryNode:
        token = self._peek()
        if token == '(':
            self._consume()
            expr = self._parse_or()
            if self._peek() == ')':
                self._consume()
            return expr
        else:
            return Term(self._consume())

