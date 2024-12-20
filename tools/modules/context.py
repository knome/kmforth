
import contextlib

class Context:
    
    def __init__(
        self ,
        log  ,
    ):
        self._log = log
        self._nextid = 0
    
    def log( self, *args, **kwargs ):
        self._log( *args, **kwargs )
    
    def next_expansion_id( self ):
        n = self._nextid
        self._nextid += 1
        return 'expansion-id[%s]' % repr(n)
    
    @contextlib.contextmanager
    def where( self, comment ):
        try:
            yield
        except Exception:
            self._log( comment )
            raise
