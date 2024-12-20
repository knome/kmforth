
from modules.macro_list import MacroList

class ExpansionRuleReverse:
    @staticmethod
    def consumes_argument():
        return True
    
    def __init__(
        self     ,
        location ,
        source   ,
        context  ,
    ):
        self._location = location
        self._source   = source
        self._context  = context
        return
    
    def variations(
        self ,
    ):
        for value in self._source.variations():
            if value.kind() != 'macrolist':
                raise Exception( '.sorted expected macrolist, found %s' % repr( value ))
            
            yield MacroList(
                location = self._location               ,
                bits     = list(reversed(value.bits())) ,
            )
