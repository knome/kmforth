
class MacroDefinition:
    def __init__(
        self                  ,
        name                  ,
        parameters            ,
        unexpandedDefinitions ,
    ):
        self._name                  = name
        self._parameters            = parameters
        self._unexpandedDefinitions = unexpandedDefinitions
        return
    
    def name( self ):
        return self._name
    
    def definition_type( self ):
        return 'macro-definition'
    
    def parameters( self ):
        return self._parameters
    
    def unexpanded_definitions( self ):
        return self._unexpandedDefinitions
