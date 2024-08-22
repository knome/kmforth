
class MacroParameter:
    def __init__(
        self     ,
        initial  ,
        namer    ,
        expander ,
    ):
        self._initial  = initial
        self._namer    = namer
        self._expander = expander
        return
    
    def __repr__(
        self ,
    ):
        return '<MacroParameter namer=%s expander=%s>' % (
            repr( self._namer    ) ,
            repr( self._expander ) ,
        )
    
    def namer( self ):
        return self._namer
    
    def expander( self ):
        return self._expander
    
    def consumes_argument( self ):
        return self._expander.consumes_argument()
    
    def simple( self ):
        return '<macro-parameter namer=%s>' % self._namer.simple()
