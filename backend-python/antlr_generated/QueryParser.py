# Generated from d:/Spillage-Search/backend-python/grammar/Query.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,7,38,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,1,0,1,0,1,0,1,1,1,1,1,1,
        5,1,15,8,1,10,1,12,1,18,9,1,1,2,1,2,1,2,1,2,5,2,24,8,2,10,2,12,2,
        27,9,2,1,3,1,3,1,3,1,3,1,3,1,3,1,3,3,3,36,8,3,1,3,0,0,4,0,2,4,6,
        0,0,38,0,8,1,0,0,0,2,11,1,0,0,0,4,19,1,0,0,0,6,35,1,0,0,0,8,9,3,
        2,1,0,9,10,5,0,0,1,10,1,1,0,0,0,11,16,3,4,2,0,12,13,5,1,0,0,13,15,
        3,4,2,0,14,12,1,0,0,0,15,18,1,0,0,0,16,14,1,0,0,0,16,17,1,0,0,0,
        17,3,1,0,0,0,18,16,1,0,0,0,19,25,3,6,3,0,20,21,5,2,0,0,21,24,3,6,
        3,0,22,24,3,6,3,0,23,20,1,0,0,0,23,22,1,0,0,0,24,27,1,0,0,0,25,23,
        1,0,0,0,25,26,1,0,0,0,26,5,1,0,0,0,27,25,1,0,0,0,28,29,5,3,0,0,29,
        36,3,6,3,0,30,31,5,4,0,0,31,32,3,2,1,0,32,33,5,5,0,0,33,36,1,0,0,
        0,34,36,5,6,0,0,35,28,1,0,0,0,35,30,1,0,0,0,35,34,1,0,0,0,36,7,1,
        0,0,0,4,16,23,25,35
    ]

class QueryParser ( Parser ):

    grammarFileName = "Query.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'OR'", "'AND'", "'NOT'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "OR", "AND", "NOT", "LPAREN", "RPAREN", 
                      "WORD", "WS" ]

    RULE_query = 0
    RULE_orExpression = 1
    RULE_andExpression = 2
    RULE_atom = 3

    ruleNames =  [ "query", "orExpression", "andExpression", "atom" ]

    EOF = Token.EOF
    OR=1
    AND=2
    NOT=3
    LPAREN=4
    RPAREN=5
    WORD=6
    WS=7

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class QueryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def orExpression(self):
            return self.getTypedRuleContext(QueryParser.OrExpressionContext,0)


        def EOF(self):
            return self.getToken(QueryParser.EOF, 0)

        def getRuleIndex(self):
            return QueryParser.RULE_query

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitQuery" ):
                return visitor.visitQuery(self)
            else:
                return visitor.visitChildren(self)




    def query(self):

        localctx = QueryParser.QueryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_query)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 8
            self.orExpression()
            self.state = 9
            self.match(QueryParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OrExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def andExpression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(QueryParser.AndExpressionContext)
            else:
                return self.getTypedRuleContext(QueryParser.AndExpressionContext,i)


        def OR(self, i:int=None):
            if i is None:
                return self.getTokens(QueryParser.OR)
            else:
                return self.getToken(QueryParser.OR, i)

        def getRuleIndex(self):
            return QueryParser.RULE_orExpression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOrExpression" ):
                return visitor.visitOrExpression(self)
            else:
                return visitor.visitChildren(self)




    def orExpression(self):

        localctx = QueryParser.OrExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_orExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 11
            self.andExpression()
            self.state = 16
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 12
                self.match(QueryParser.OR)
                self.state = 13
                self.andExpression()
                self.state = 18
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AndExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atom(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(QueryParser.AtomContext)
            else:
                return self.getTypedRuleContext(QueryParser.AtomContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(QueryParser.AND)
            else:
                return self.getToken(QueryParser.AND, i)

        def getRuleIndex(self):
            return QueryParser.RULE_andExpression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAndExpression" ):
                return visitor.visitAndExpression(self)
            else:
                return visitor.visitChildren(self)




    def andExpression(self):

        localctx = QueryParser.AndExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_andExpression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19
            self.atom()
            self.state = 25
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 92) != 0):
                self.state = 23
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [2]:
                    self.state = 20
                    self.match(QueryParser.AND)
                    self.state = 21
                    self.atom()
                    pass
                elif token in [3, 4, 6]:
                    self.state = 22
                    self.atom()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 27
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return QueryParser.RULE_atom

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class NotAtomContext(AtomContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a QueryParser.AtomContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NOT(self):
            return self.getToken(QueryParser.NOT, 0)
        def atom(self):
            return self.getTypedRuleContext(QueryParser.AtomContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNotAtom" ):
                return visitor.visitNotAtom(self)
            else:
                return visitor.visitChildren(self)


    class WordAtomContext(AtomContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a QueryParser.AtomContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def WORD(self):
            return self.getToken(QueryParser.WORD, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWordAtom" ):
                return visitor.visitWordAtom(self)
            else:
                return visitor.visitChildren(self)


    class ParenAtomContext(AtomContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a QueryParser.AtomContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LPAREN(self):
            return self.getToken(QueryParser.LPAREN, 0)
        def orExpression(self):
            return self.getTypedRuleContext(QueryParser.OrExpressionContext,0)

        def RPAREN(self):
            return self.getToken(QueryParser.RPAREN, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParenAtom" ):
                return visitor.visitParenAtom(self)
            else:
                return visitor.visitChildren(self)



    def atom(self):

        localctx = QueryParser.AtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_atom)
        try:
            self.state = 35
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [3]:
                localctx = QueryParser.NotAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 28
                self.match(QueryParser.NOT)
                self.state = 29
                self.atom()
                pass
            elif token in [4]:
                localctx = QueryParser.ParenAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 30
                self.match(QueryParser.LPAREN)
                self.state = 31
                self.orExpression()
                self.state = 32
                self.match(QueryParser.RPAREN)
                pass
            elif token in [6]:
                localctx = QueryParser.WordAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 34
                self.match(QueryParser.WORD)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





