
class Source:
    def __init__(
        self   ,
        source ,
    ):
        self._iterator = iter( source )
        self._pending  = None
        self._done     = False
    
    def peek(
        self ,
    ):
        if self._done:
            return None
        elif self._pending == None:
            self._pending = next( self._iterator, None )
            if self._pending == None:
                self._done = True
        
        return self._pending
    
    def take(
        self ,
    ):
        vv = self.peek()
        self._pending = None
        return vv

