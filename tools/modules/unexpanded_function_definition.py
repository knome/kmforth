
class UnexpandedFunctionDefinition:
    def __init__(
        self          ,
        initial       ,
        bits          ,
        currentModule ,
    ):
        self._initial       = initial
        self._bits          = bits
        self._currentModule = currentModule
        return
    
    def initial( self ):
        return self._initial
    
    def bits( self ):
        return self._bits
    
    def current_module( self ):
        return self._currentModule
