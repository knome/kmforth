
from modules.token import Token

class ExpansionRuleLength:
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
            if value.kind() != 'string':
                raise Exception( '.length expected string, found %s' % repr( value ) )
            
            cc = len( value.value() )
            
            yield Token(
                location = self._location ,
                kind     = 'integer'      ,
                value    = cc             ,
            )
