
class ExpansionRuleFirst:
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
    
    def variations(
        self ,
    ):
        for value in self._source.variations():
            if value.kind() != 'macrolist':
                raise Exception( '.first expected a macrolist, found %s' % repr( value ) )
            
            if value.bits():
                yield value.bits()[0]
            else:
                raise Exception( '.first received a macrolist with no entries: %s' % repr( value ) )
