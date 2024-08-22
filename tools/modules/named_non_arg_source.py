
class NamedNonArgSource:
    def __init__(
        self     ,
        namer    ,
        expander ,
    ):
        self._namer    = namer
        self._expander = expander
        return
    
    def namer(
        self ,
    ):
        return self._namer
    
    def variations(
        self ,
    ):
        return self._expander.non_argument_consuming_variations()
