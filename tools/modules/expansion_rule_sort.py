
from modules.macro_list import MacroList

class ExpansionRuleSort:
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
                raise Exception( '.sorted expected macrolist, found %s' % repr( value ))
            
            yield MacroList(
                location = self._location                                ,
                bits     = list(sorted(value.bits(), key = self._keyfn)) ,
            )
    
    @staticmethod
    def _keyfn(v):
        if v.kind() == 'token':
            raise Exception('wat %s' % repr(v))
            return ('token', v.value())
        elif v.kind() == 'macrolist':
            return ('macrolist', tuple(self._keyfn(v) for v in v.bits()))
        elif v.kind() == 'integer':
            return ('integer', v.value())
        else:
            raise Exception('unknown type in keyfn: %s' % repr(v))
