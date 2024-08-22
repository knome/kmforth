
class Character:
    def __init__(
        self      ,
        location  ,
        character ,
    ):
        self._location  = location
        self._character = character
        return
    
    def __repr__(
        self ,
    ):
        return '<Character character=%s>' % repr( self._character )
    
    def location  ( self ): return self._location
    def character ( self ): return self._character
