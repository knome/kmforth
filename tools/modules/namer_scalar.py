
class NamerScalar:
    def __init__(
        self ,
        name ,
    ):
        self._name = name
    
    def names( self, value ):
        yield (self._name, value)
        
    def simple( self ):
        return '<scalar-namer %s>' % repr( self._name )
