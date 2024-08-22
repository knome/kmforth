
class MacroList:
    def __init__(
        self     ,
        location ,
        bits     ,
    ):
        self._location = location
        self._bits     = bits
    
    def __repr__(
        self ,
    ):
        return '<MacroList contents=%s>' % repr( self._bits )
    
    def simple(
        self ,
    ):
        return '( %s )' % (
            ' '.join( str( bit.simple() ) for bit in self._bits ) ,
        )
    
    def kind( self ):
        return 'macrolist'
    
    def location( self ):
        return self._location
    
    def bits( self ):
        return self._bits
