
class ExpansionRuleEach:
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
            
            if value.kind() != 'macrolist':
                raise Exception( '.each expected macrolist, found: %s' % repr( value ) )
            
            for bit in value.bits():
                yield bit
