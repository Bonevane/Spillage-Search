# Generated from d:/Spillage-Search/backend-python/grammar/Query.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .QueryParser import QueryParser
else:
    from QueryParser import QueryParser

# This class defines a complete generic visitor for a parse tree produced by QueryParser.

class QueryVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by QueryParser#query.
    def visitQuery(self, ctx:QueryParser.QueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QueryParser#orExpression.
    def visitOrExpression(self, ctx:QueryParser.OrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QueryParser#andExpression.
    def visitAndExpression(self, ctx:QueryParser.AndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QueryParser#NotAtom.
    def visitNotAtom(self, ctx:QueryParser.NotAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QueryParser#ParenAtom.
    def visitParenAtom(self, ctx:QueryParser.ParenAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QueryParser#WordAtom.
    def visitWordAtom(self, ctx:QueryParser.WordAtomContext):
        return self.visitChildren(ctx)



del QueryParser