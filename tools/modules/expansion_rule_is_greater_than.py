
from modules.token import Token

class ExpansionRuleIsGreaterThan:
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
                raise Exception( '.isGreaterThan expected a macrolist, found %s' % repr( value ) )
            
            last = None
            isGreater = True
            for bit in value.bits():
                if bit.kind() != 'integer':
                    raise Exception( '.isGreaterThan expected macrolist to contain integers, found %s' % repr( bit ) )
                elif last == None:
                    last = bit
                else:
                    if not ( last.value() > bit.value() ):
                        isGreater = False
                        break
            
            yield Token(
                location = self._location        ,
                kind     = 'integer'             ,
                value    = 1 if isGreater else 0 ,
            )
