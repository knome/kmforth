
class ExpansionRuleToOne:
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
                raise Exception( '.toOne received non-integer: %s' % repr( value ) )
            new = value.value()
            if new > 1:
                while new >= 1:
                    yield Token(
                        location = value.location() ,
                        kind     = 'integer'        ,
                        value    = new              ,
                    )
                    new -= 1
