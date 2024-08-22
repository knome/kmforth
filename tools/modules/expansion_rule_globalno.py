
class ExpansionRuleGlobalNo:
    NN = [1]
    
    @staticmethod
    def consumes_argument():
        return False
    
    def __init__(
        self     ,
        location ,
    ):
        self._location = location
    
    def variations( self ):
        nn = self.NN[0]
        self.NN[0] += 1
        yield Token(
            location = self._location ,
            kind     = 'integer'      ,
            value    = nn             ,
        )
