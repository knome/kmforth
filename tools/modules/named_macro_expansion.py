
class NamedMacroExpansion:
    def __init__(
        self      ,
        initial   ,
        macroName ,
        arguments ,
    ):
        self._initial   = initial
        self._macroName = macroName
        self._arguments = arguments
        return
    
    def __repr__(
        self ,
    ):
        return '<NamedMacroExpansion name=%s arguments=%s>' % (
            repr( self._macroName ) ,
            repr( self._arguments ) ,
        )
    
    def simple(
        self ,
    ):
        return '@ %s ( %s )' % (
            self._macroName.simple()                            ,
            ' '.join( arg.simple() for arg in self._arguments ) ,
        )
    
    def initial( self ):
        return self._initial
    
    def definition_type( self ):
        return 'named-macro-expansion'
    
    def macro_name( self ):
        return self._macroName
    
    def arguments( self ):
        return self._arguments
