
# gathers all variations of its source into a macrolist
class ExpansionRuleCollect:
    @staticmethod
    def consumes_argument():
        return True
    
    def __init__(
        self     ,
        location ,
        source   ,
    ):
        self._location = location
        self._source   = source
        return
    
    def variations(
        self ,
    ):
        bits = []
        for value in self._source.variations():
            bits.append( value )
        
        yield MacroList(
            location = self._location ,
            bits     = bits           ,
        )
