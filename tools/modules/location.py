
class Location:
    def __init__(
        self     ,
        fileno   ,
        filename ,
        line     ,
        column   ,
    ):
        self._fileno   = fileno
        self._filename = filename
        self._line     = line
        self._column   = column

    def __repr__(
        self
    ):
        return '(%s:%s:%s)' % (
            self._filename ,
            self._line     ,
            self._column   ,
        )
    
    def fileno   ( self ): return self._fileno
    def filename ( self ): return self._filename
    def line     ( self ): return self._line
    def column   ( self ): return self._column
