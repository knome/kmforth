
class ExpansionRuleIfNotEmpty:
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
        
    def variations(
        self ,
    ):
        for value in self._source.variations():
            if value.kind() != 'macrolist':
                raise Exception( '.ifNotEmpty expected a macrolist, found %s' % repr( value ) )
            
            if value.bits():
                yield value
