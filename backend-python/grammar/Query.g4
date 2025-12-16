grammar Query;

// Parser Rules
query: orExpression EOF;

orExpression
    : andExpression (OR andExpression)*
    ;

andExpression
    : atom (AND atom | atom)*
    ;

atom
    : NOT atom              # NotAtom
    | LPAREN orExpression RPAREN # ParenAtom
    | WORD                  # WordAtom
    ;

// Lexer Rules
OR: 'OR';
AND: 'AND';
NOT: 'NOT';
LPAREN: '(';
RPAREN: ')';
WORD: [a-zA-Z0-9_]+;
WS: [ \t\r\n]+ -> skip;
