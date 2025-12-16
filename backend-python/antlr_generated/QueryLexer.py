# Generated from d:/Spillage-Search/backend-python/grammar/Query.g4 by ANTLR 4.13.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,7,42,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,
        6,7,6,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,3,1,3,1,4,1,
        4,1,5,4,5,32,8,5,11,5,12,5,33,1,6,4,6,37,8,6,11,6,12,6,38,1,6,1,
        6,0,0,7,1,1,3,2,5,3,7,4,9,5,11,6,13,7,1,0,2,4,0,48,57,65,90,95,95,
        97,122,3,0,9,10,13,13,32,32,43,0,1,1,0,0,0,0,3,1,0,0,0,0,5,1,0,0,
        0,0,7,1,0,0,0,0,9,1,0,0,0,0,11,1,0,0,0,0,13,1,0,0,0,1,15,1,0,0,0,
        3,18,1,0,0,0,5,22,1,0,0,0,7,26,1,0,0,0,9,28,1,0,0,0,11,31,1,0,0,
        0,13,36,1,0,0,0,15,16,5,79,0,0,16,17,5,82,0,0,17,2,1,0,0,0,18,19,
        5,65,0,0,19,20,5,78,0,0,20,21,5,68,0,0,21,4,1,0,0,0,22,23,5,78,0,
        0,23,24,5,79,0,0,24,25,5,84,0,0,25,6,1,0,0,0,26,27,5,40,0,0,27,8,
        1,0,0,0,28,29,5,41,0,0,29,10,1,0,0,0,30,32,7,0,0,0,31,30,1,0,0,0,
        32,33,1,0,0,0,33,31,1,0,0,0,33,34,1,0,0,0,34,12,1,0,0,0,35,37,7,
        1,0,0,36,35,1,0,0,0,37,38,1,0,0,0,38,36,1,0,0,0,38,39,1,0,0,0,39,
        40,1,0,0,0,40,41,6,6,0,0,41,14,1,0,0,0,3,0,33,38,1,6,0,0
    ]

class QueryLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    OR = 1
    AND = 2
    NOT = 3
    LPAREN = 4
    RPAREN = 5
    WORD = 6
    WS = 7

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'OR'", "'AND'", "'NOT'", "'('", "')'" ]

    symbolicNames = [ "<INVALID>",
            "OR", "AND", "NOT", "LPAREN", "RPAREN", "WORD", "WS" ]

    ruleNames = [ "OR", "AND", "NOT", "LPAREN", "RPAREN", "WORD", "WS" ]

    grammarFileName = "Query.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


