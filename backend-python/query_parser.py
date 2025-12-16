from abc import ABC, abstractmethod
from typing import List, Set, Optional, Any
from dataclasses import dataclass
from antlr4 import InputStream, CommonTokenStream, ParseTreeVisitor # type: ignore
from antlr4.error.ErrorListener import ErrorListener # type: ignore

# Import generated ANTLR classes
# We use a try-except block to handle cases where generation hasn't happened yet
try:
    from antlr_generated.QueryLexer import QueryLexer
    from antlr_generated.QueryParser import QueryParser as AntlrQueryParser
    from antlr_generated.QueryVisitor import QueryVisitor
except ImportError:
    print("Warning: ANTLR generated files not found. Please run generation.")
    QueryLexer = None # type: ignore
    AntlrQueryParser = None # type: ignore
    QueryVisitor = object # type: ignore

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
# We now use ANTLR4 for parsing.
# Grammar is defined in grammar/Query.g4

class ASTBuilderVisitor(QueryVisitor):
    """
    Converts ANTLR Parse Tree to our custom QueryNode AST.
    """
    def visitQuery(self, ctx: AntlrQueryParser.QueryContext) -> QueryNode:
        return self.visit(ctx.orExpression())

    def visitOrExpression(self, ctx: AntlrQueryParser.OrExpressionContext) -> QueryNode:
        # orExpression : andExpression (OR andExpression)*
        exprs = [self.visit(child) for child in ctx.andExpression()]
        if not exprs:
            return Term("")
        
        result = exprs[0]
        for i in range(1, len(exprs)):
            result = Or(result, exprs[i])
        return result

    def visitAndExpression(self, ctx: AntlrQueryParser.AndExpressionContext) -> QueryNode:
        # andExpression : atom (AND atom | atom)*
        # Note: The grammar structure means we just visit all atoms and AND them together
        atoms = [self.visit(child) for child in ctx.atom()]
        if not atoms:
            return Term("")
            
        result = atoms[0]
        for i in range(1, len(atoms)):
            result = And(result, atoms[i])
        return result

    def visitNotAtom(self, ctx: AntlrQueryParser.NotAtomContext) -> QueryNode:
        return Not(self.visit(ctx.atom()))

    def visitParenAtom(self, ctx: AntlrQueryParser.ParenAtomContext) -> QueryNode:
        return self.visit(ctx.orExpression())

    def visitWordAtom(self, ctx: AntlrQueryParser.WordAtomContext) -> QueryNode:
        return Term(ctx.getText())

class ThrowingErrorListener(ErrorListener):
    def syntaxError(self, recognizer: Any, offendingSymbol: Any, line: int, column: int, msg: str, e: Any) -> None:
        raise Exception(f"Syntax Error at line {line}:{column} - {msg}")

class QueryParser:
    """
    A parser for search queries using ANTLR4.
    """
    def __init__(self, query_str: str):
        self.query_str = query_str

    def parse(self) -> QueryNode:
        if not self.query_str.strip():
            return Term("")

        # Setup ANTLR pipeline
        input_stream = InputStream(self.query_str)
        lexer = QueryLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(ThrowingErrorListener())
        
        stream = CommonTokenStream(lexer)
        parser = AntlrQueryParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(ThrowingErrorListener())
        
        # Parse
        tree = parser.query()
        
        # Build AST
        visitor = ASTBuilderVisitor()
        return visitor.visit(tree)


