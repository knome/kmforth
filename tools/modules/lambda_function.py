
from modules.token import Token

class LambdaFunction:
    
    def rewriting_commands( self, new ):
        return LambdaFunction(
            location   = self._location                       ,
            lambdaName = self._lambdaName                     ,
            parent     = self._parent                         ,
            body       = self._body.rewriting_commands( new ) ,
        )
    
    def rewriting_locals( self, new ):
        return LambdaFunction(
            location   = self._location                     ,
            lambdaName = self._lambdaName                   ,
            parent     = self._parent                       ,
            body       = self._body.rewriting_locals( new ) ,
        )
    
    def rewriting_parent( self, new ):
        return LambdaFunction(
            location   = self._location   ,
            lambdaName = self._lambdaName ,
            parent     = new              ,
            body       = self._body       ,
        )
    
    def rewriting_name( self, new ):
        return LambdaFunction(
            location   = self._location ,
            lambdaName = new            ,
            parent     = self._parent   ,
            body       = self._body     ,
        )
    
    def rewriting_nonlocals( self, varupdates ):
        return LambdaFunction(
            location   = self._location   ,
            lambdaName = self._lambdaName ,
            parent     = self._parent     ,
            body       = self._body.rewriting_nonlocals( self._lambdaName, varupdates ),
        )
    
    def rewriting_subfns( self, updates ):
        return LambdaFunction(
            location   = self._location   ,
            lambdaName = self._lambdaName ,
            parent     = self._parent     ,
            body       = self._body.rewriting_subfns(updates),
        )
    
    def __init__(
        self       ,
        location   ,
        lambdaName ,
        body       ,
        parent     ,
    ):
        self._location   = location
        self._lambdaName = lambdaName
        self._body       = body
        self._parent     = parent
        return
    
    def __repr__( self ):
        return '<LambdaFunction %s name=%s commands=%d>' % (
            repr( self._location )       ,
            self.name()                  ,
            len( self._body.body_details(self._lambdaName).commands() ) ,
        )
    
    def kind( self ): return 'lambda'
    
    def location ( self ): return self._location
    def body     ( self ): return self._body.body_details(self._lambdaName)
    def parent   ( self ): return self._parent
        
    def is_closure( self, functions ):
        return self._body.body_details(self._lambdaName).is_closure( functions )
    
    def name( self ):
        return Token(
            location = self._location  ,
            kind   = 'word'            ,
            value  = self._lambdaName ,
        )
