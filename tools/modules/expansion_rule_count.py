
from modules.token import Token

class ExpansionRuleCount:
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
                raise Exception( '.count expected macrolist, found %s' % repr( value ) )
            
            cc = len( list( value.bits() ) )
            
            yield Token(
                location = self._location ,
                kind     = 'integer'      ,
                value    = cc             ,
            )
