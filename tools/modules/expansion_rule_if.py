
from modules.token import Token

class ExpansionRuleIf:
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
            if value.kind() in ['integer', 'string']:
                if value.value():
                    yield Token(
                        location = self._location            ,
                        kind     = 'integer'                 ,
                        value    = 1 if value.value() else 0 ,
                    )
                else:
                    # don't trigger an expansion on false
                    pass
            else:
                raise Exception(
                    'unknown value for .if: %s' % repr(value)
                )
