
from modules.token    import Token
from modules.mangling import mangle

class NamedFunction:
    
    def rewriting_commands( self, new ):
        return NamedFunction(
            location = self._location                       ,
            name     = self._name                           ,
            body     = self._body.rewriting_commands( new ) ,
        )
    
    def rewriting_locals( self, new ):
        return NamedFunction(
            location = self._location                     ,
            name     = self._name                         ,
            body     = self._body.rewriting_locals( new ) ,
        )
    
    def rewriting_parent( self, new ):
        raise Exception( 'cannot change parent of nonclosure' )
    
    def __init__(
        self        ,
        location    ,
        name        ,
        body        ,
    ):
        self._location = location
        self._name     = name
        self._body     = body
        return
    
    def __repr__( self ):
        return '<NamedFunction name=%s commands=%s>' % (
            repr( self._name.value() ) ,
            repr( len( self._body.body_details(self._name.value()).commands() ) ) ,
        )
    
    def simple( self ):
        return ': %s %s ;' % (
            self._name.simple()                                       ,
            ' '.join( bit.simple() for bit in self._body.commands() ) ,
        )
    
    def definition_type( self ):
        return 'function'
    
    def location ( self ): return self._location
    def body     ( self ): return self._body.body_details(self._name.value())
    def parent   ( self ): return None
    
    def name( self ):
        return Token(
            location = self._name.location()            ,
            kind   = 'word'                             ,
            value  = mangle( ':' + self._name.value() ) ,
        )
