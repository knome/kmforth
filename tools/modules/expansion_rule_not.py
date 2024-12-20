
from modules.token import Token

class ExpansionRuleNot:
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
    
    def _is_falsy(
        self  ,
        value ,
    ):
        if value.kind() == 'integer':
            return value.value() == 0
            
        elif value.kind() == 'string':
            return value.value() == ""
            
        elif value.kind() == 'macrolist':
            return not list(value.bits())
            
        else:
            raise Exception('unsure how to .not value: %s' % repr(value))
    
    def variations(
        self ,
    ):
        for value in self._source.variations():
            yield Token(
                location = self._location                    ,
                kind     = 'integer'                         ,
                value    = 1 if self._is_falsy(value) else 0 ,
            )
