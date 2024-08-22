
class ExpansionRuleToZero:
    @staticmethod
    def consumes_argument():
        return True
    
    def __init__(
        self     ,
        location ,
        source   ,
    ):
        self._location = location
        self._source   = source
        
    def variations( self ):
        
        for value in self._source.variations():
            
            if value.kind() != 'integer':
                raise Exception( '.toZero received non-integer: %s' % repr( value ) )
            
            new = value.value() - 1
            
            if new > 0:
                while new >= 0:
                    yield Token(
                        location = value.location() ,
                        kind     = 'integer'        ,
                        value    = new              ,
                    )
                    new -= 1
