
class ExpansionRuleExpandIf:
    # truthiness: anything not 0 () or ""
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
            if value.kind() == 'integer':
                if value.value():
                    yield value
            elif value.kind() == 'string':
                if value.value():
                    yield value
            elif value.kind() == 'macrolist':
                if value.bits():
                    yield value
            else:
                raise Exception( '.expandIf expects integers, strings or macrolists, found %s' % repr( value ) )
