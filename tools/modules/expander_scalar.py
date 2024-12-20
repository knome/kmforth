
from modules.variations import Variations

class ExpanderScalar:
    def __init__(
        self    ,
        context ,
    ):
        self._context        = context
        self._expansionRules = []
        return
    
    def expansion_rules( self ):
        for rule, location in self._expansionRules:
            yield rule
    
    def add_expansion_rule( self, rule, location ):
        return self._expansionRules.append( (rule, location) )
    
    def consumes_argument( self ):
        if not self._expansionRules:
            return True
        else:
            return self._expansionRules[0][0].consumes_argument()
    
    def argument_consuming_variations( self, value ):
        source = Variations( value )
        for rule, location in self._expansionRules:
            source = rule(
                location = location      ,
                source   = source        ,
                context  = self._context ,
            )
        
        for variation in source.variations():
            yield variation
    
    def non_argument_consuming_variations( self ):
        if self.consumes_argument():
            raise Exception( 'nonconsuming variations should not be called for an argument consuming parameter' )
        else:
            rule, location = self._expansionRules[0]
            source = rule(
                location = location       ,
                context  = self._context  ,
            )
            for rule, location in self._expansionRules[1:]:
                source = rule(
                    location = location      ,
                    source   = source        ,
                    context  = self._context ,
                )
            
            for variation in source.variations():
                yield variation
