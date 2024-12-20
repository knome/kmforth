
from modules.macro_list import MacroList

class ExpansionRuleRest:
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
    
    def variations(
        self ,
    ):
        for value in self._source.variations():
            if value.kind() != 'macrolist':
                raise Exception( '.rest expected a macrolist, found %s' % repr( value ) )
            
            if value.bits():
                yield MacroList(
                    location = value.location() ,
                    bits     = value.bits()[1:] ,
                )
            else:
                raise Exception( '.rest received a macrolist with no entries: %s' % repr( value ) )
