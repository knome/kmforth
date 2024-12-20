
# due to the way expansion currently operates, this doesn't do anything at all
# it either spits out a single 0 which is used and reused by the following parameter expansions
#   or it is instantiated anew for each combination of other parameter expansions.
# to make it useful, it would need to be able to access data from the expansion process
#   we'll need to introduce some way for it to communicate with the code performing the
#   expansions at that location.
# I don't care right now, so I'll just leave this reminder
class ExpansionRuleExpandNo:
    @staticmethod
    def consumes_argument():
        return False
    
    def __init__(
        self     ,
        location ,
        context  ,
    ):
        self._location = location
        self._context  = context
        self._nn       = 0
    
    def variations( self ):
        nn = self._nn
        self._nn += 1
        
        yield Token(
            location = self._location ,
            kind     = 'integer'      ,
            value    = nn             ,
        )
