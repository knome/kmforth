
NUMBERS  = set( '0123456789' )
LETTERS  = set( 'abcdefghijklmnopqrstuvzwxyz' )

WORDSTART = LETTERS.union( set('_+-/*<>-%=.@!~') )
WORDBITS  = WORDSTART.union( NUMBERS )

STRUCTBITS = ':;[]{}()'
