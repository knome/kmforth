
class Uniques:
    def __init__(
        self ,
    ):
        self._next = 0
    
    def get( self ):
        v = self._next
        self._next += 1
        return v
