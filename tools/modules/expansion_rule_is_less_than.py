
class ExpansionRuleIsLessThan:
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
                raise Exception( '.isLessThan expected a macrolist, found %s' % repr( value ) )
            
            last = None
            isLesser = True
            for bit in value.bits():
                if bit.kind() != 'integer':
                    raise Exception( '.isLessThan expected macrolist to contain integers, found %s' % repr( bit ) )
                elif last == None:
                    last = bit
                else:
                    if not ( last.value() < bit.value() ):
                        isLesser = False
                        break
            
            yield Token(
                location = self._location       ,
                kind     = 'integer'            ,
                value    = 1 if isLesser else 0 ,
            )
