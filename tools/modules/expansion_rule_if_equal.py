
class ExpansionRuleIfEqual:
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
                raise Exception( '.ifEqual expected a macrolist, found %s' % repr( value ) )
            
            last    = None
            isEqual = True
            for bit in value.bits():
                if bit.kind() not in [ 'string', 'integer' ]:
                    raise Exception( '.ifEqual only operates on macrolists of strings and integers, found %s' % repr( bit ) )
                if last == None:
                    last = bit
                else:
                    if bit.kind() != last.kind():
                        raise Exception( '.ifEqual does not allow mixing integers and strings, found %s after %s' % (
                            repr( bit     ) ,
                            repr( lastBit ) ,
                        ))
                    elif bit.value() == last.value():
                        # good
                        continue
                    else:
                        isEqual = False
                        break
            
            if isEqual:
                yield value
