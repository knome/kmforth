
class NamedArgSource:
    def __init__(
        self     ,
        namer    ,
        expander ,
        source   ,
    ):
        self._namer    = namer
        self._expander = expander
        self._source   = source
        return
    
    def namer(
        self ,
    ):
        return self._namer
    
    def variations(
        self ,
    ):
        return self._expander.argument_consuming_variations( self._source )
