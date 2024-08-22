
class ExpansionRuleExpandIfNot:
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
                if not value.value():
                    yield value
            elif value.kind() == 'string':
                if not value.value():
                    yield value
            elif value.kind() == 'macrolist':
                if not value.bits():
                    yield value
            else:
                raise Exception( '.expandIf expects integers, strings or macrolists, found %s' % repr( value ) )
