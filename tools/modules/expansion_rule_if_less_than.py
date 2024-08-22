
class ExpansionRuleIfLessThan:
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
                raise Exception( '.ifLessThan expected a macrolist, found %s' % repr( value ) )
            
            last = None
            isLesser = True
            for bit in value.bits():
                if bit.kind() != 'integer':
                    raise Exception( '.ifLessThan expected macrolist to contain integers, found %s' % repr( bit ) )
                elif last == None:
                    last = bit
                else:
                    if not ( last.value() < bit.value() ):
                        isLesser = False
                        break
            
            if isLesser:
                yield value
