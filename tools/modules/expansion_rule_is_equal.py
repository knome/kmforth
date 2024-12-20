
from modules.token import Token

class ExpansionRuleIsEqual:
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
        return
    
    def variations(
        self ,
    ):
        for value in self._source.variations():
            if value.kind() != 'macrolist':
                raise Exception( '.isEqual expected a macrolist, found %s' % repr( value ) )
            last    = None
            isEqual = True
            for bit in value.bits():
                if bit.kind() not in [ 'string', 'integer' ]:
                    raise Exception( '.isEqual only operates on macrolists of strings and integers, found %s' % repr( bit ) )
                if last == None:
                    last = bit
                else:
                    if bit.kind() != last.kind():
                        raise Exception( '.isEqual does not allow mixing integers and strings, found %s after %s' % (
                            repr( bit     ) ,
                            repr( lastBit ) ,
                        ))
                    elif bit.value() == last.value():
                        # good
                        continue
                    else:
                        isEqual = False
                        break
            
            yield Token(
                location = self._location      ,
                kind     = 'integer'           ,
                value    = 1 if isEqual else 0 ,
            )
