
class ExpansionRuleDecr:
    
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
    
    def variations( self ):
        for value in self._source.variations():
            if value.kind() != 'integer':
                raise Exception( '.decr received non-integer: %s' % repr( value ) )
            else:
                new = value.value() - 1
                yield Token(
                    location = value.location() ,
                    kind     = 'integer'        ,
                    value    = new              ,
                )
