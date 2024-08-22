
class StringCoalescer:
    def __init__(
        self ,
    ):
        self._string2label = {}
        return
    
    def lookup( self, ss ):
        return self._string2label.get( ss, None )
        
    def remember( self, ss, label ):
        self._string2label[ ss ] = label
