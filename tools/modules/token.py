
class Token:
    def __init__(
        self     ,
        location ,
        kind     ,
        value    ,
    ):
        self._location = location
        self._kind     = kind
        self._value    = value
        return
    
    def location ( self ): return self._location
    def kind     ( self ): return self._kind
    def value    ( self ): return self._value
    
    def __repr__( self ):
        return '<Token %s kind=%s value=%s>' % (
            repr( self._location ),
            repr( self._kind     ),
            repr( self._value    ),
        )
    
    def simple( self ):
        if self.kind() == 'string':
            return repr( self._value )
        elif self.kind() == 'code':
            return '`' + repr( self._value )[1:-1] + '`'
        elif self._value == None:
            return self._kind
        else:
            return str(self._value)
