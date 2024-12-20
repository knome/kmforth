
from modules.token import Token

class ExpansionRuleString:
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
            if value.kind() == 'string':
                yield value 
            elif value.kind() == 'integer':
                yield Token(
                    location = self._location     ,
                    kind     = 'string'           ,
                    value    = str(value.value()) ,
                )
            elif value.kind() == 'word':
                yield Token(
                    location = self._location ,
                    kind     = 'string'       ,
                    value    = value.value()  ,
                )
            else:
                raise Exception('.string unknown value to stringize: %s' % repr(value))
