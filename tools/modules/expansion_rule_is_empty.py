
from modules.token import Token

class ExpansionRuleIsEmpty:
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
                raise Exception( '.ifNotEmpty expected a macrolist, found %s' % repr( value ) )
            
            yield Token(
                location = self._location           ,
                kind     = 'integer'                ,
                value    = 0 if value.bits() else 1 ,
            )
