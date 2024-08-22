
import contextlib

class Context:
    
    def __init__(
        self ,
        log  ,
    ):
        self._log = log
    
    @contextlib.contextmanager
    def where( self, comment ):
        try:
            yield
        except Exception:
            self._log( comment )
            raise
