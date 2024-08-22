
import os.path

class FileSource:
    
    NN = 0
    
    def __init__(
        self        ,
        origin      ,
        cwd         ,
        path        ,
        libraryPath ,
    ):
        self._fileno = self.NN
        self.NN += 1
        
        self._origin      = origin
        self._cwd         = cwd
        self._path        = path
        self._libraryPath = libraryPath
        return
    
    def fileno( self ):
        return self._fileno
    
    def definition_type( self ):
        return 'include'
    
    def path(
        self ,
    ):
        if (
            self._path.startswith('/')
            or
            self._path.startswith('./')
            or
            self._path.startswith('../')
        ):
            initial = os.path.join(
                self._cwd  ,
                self._path ,
            )
        else:
            initial = os.path.join(
                self._libraryPath ,
                self._path        ,
            )
        
        if os.path.isdir( initial ):
            full = initial + '/default'
            if os.path.isdir( full ):
                raise Exception( 'default in a directory import cannot itself be a directory: %s' % repr( full ) )
        else:
            full = initial
        
        return full
    
    def cwd_for_includes(
        self, 
    ):
        return os.path.dirname( self.path() )
    
    def library_path(
        self ,
    ):
        return self._libraryPath
    
    def read_source(
        self ,
    ):
        try:
            with open( self.path() ) as ff:
                data = ff.read()
                return data
        except Exception as ee:
            raise Exception( 'error reading path=%s %s: %s, %s' % (
                repr( self._path )  ,
                str( self._origin ) ,
                str( type( ee ) )   ,
                str( ee )           ,
            ))
