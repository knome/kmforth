
import optparse

from modules.mangling import mangle

class Options:
    def __init__(
        self     ,
        **kwargs
    ):
        for (k,v) in kwargs.items():
            setattr(self, k, v)

def parse_options(
    args                  ,
    defaultImplementation ,
):
    
    parser = optparse.OptionParser()
    
    parser.add_option(
        '--generate'    ,
        dest='generate' ,
        default='code'  ,
    )
    
    parser.add_option(
        '--library-path'    ,
        dest='libraryPath'  ,
        default='./library' ,
    )
    
    parser.add_option(
        '--show-expansions'   ,
        action='store_true'   ,
        dest='showExpansions' ,
        default=False         ,
    )
    
    parser.add_option(
        '--optimize'        ,
        action='store_true' ,
        dest='optimize'     ,
        default=False       ,
    )
    
    parser.add_option(
        '--show-optimizations'   ,
        action='store_true'      ,
        dest='showOptimizations' ,
        default=False            ,
    )
    
    parser.add_option(
        '--debug-optimizations',
        action='store_true',
        dest='debugOptimizations',
        default=False,
    )
    
    parser.add_option(
        '--inline-only',
        dest='inlineOnly',
    )
    
    parser.add_option(
        '--inline-except',
        dest='inlineExcept',
    )
    
    parser.add_option(
        '--startname'     ,
        dest='startname'  ,
        default=':_start' ,
    )
    
    # not guaranteed to be the same on your box!
    parser.add_option(
        '--trampoline-size',
        dest='trampolineSize',
        default='32',
    )
    
    parser.add_option(
        '--trampoline-end-offset',
        dest='trampolineEndOffset',
        default='8',
    )
    
    options, free = parser.parse_args()
    
    if len( free ) != 1:
        return None, 'usage: kmforth <path/to/file/to/compile>'
    
    if free[0] == "":
        return None, 'empty target path'
    
    if free[0] == "-":
        free[0] = "/dev/stdin"
    
    if options.startname == "":
        return None, 'must specify startname'
    
    startname = mangle( options.startname )
    
    out = Options(
        # compilation options
        libraryPath         = options.libraryPath         ,
        targetPath          = free[0]                     ,
        startname           = startname                   ,
        generate            = options.generate            ,
        # architecture options
        implementation      = defaultImplementation       ,
        trampolineSize      = options.trampolineSize      ,
        trampolineEndOffset = options.trampolineEndOffset ,
        # optimization options
        optimize            = options.optimize            ,
        inlineOnly          = options.inlineOnly          ,
        inlineExcept        = options.inlineExcept        ,
        inlineThreshold     = 10                          ,
        # debugging options
        showExpansions      = options.showExpansions      ,
        showOptimizations   = options.showOptimizations   ,
        debugOptimizations  = options.debugOptimizations  ,
    )
    
    return out, None
