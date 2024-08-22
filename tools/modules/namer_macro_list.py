
class NamerMacroList:
    def __init__(
        self          ,
        parameterList ,
    ):
        self._parameterList = parameterList
        return
    
    def names( self, value ):
        
        if value.kind() != 'macrolist':
            raise Exception( 'expected a macrolist, got: %s' % repr( value ) )
        
        if len( self._parameterList ) != len( value.bits() ):
            raise Exception( 'during expansion macro-list should have %s slots, instead found: %s' % (
                str( len( self._parameterList ) ) ,
                repr( value )                     ,
            ))
        
        for pp, vv in zip( self._parameterList, value.bits() ):
            for naming in pp.namer().names( vv ):
                yield naming
    
    def simple( self ):
        return '<macrolist-namer %s>' % repr([ pp.namer().simple() for pp in self._parameterList ])
