
import os

from modules.filesource   import FileSource
from modules.macrocontext import MacroContext
from modules.uniques      import Uniques
from modules.scanner      import Scanner
from modules.source       import Source

class CompilationManager:
    
    def __init__(
        self    ,
        options ,
        context ,
        parser  ,
    ):
        self._options = options
        self._context = context
        self._parser  = parser
    
    def compile_program(
        self       ,
        options    ,
        targetPath ,
    ):
        seen    = set()
        pending = [ FileSource(
            origin      = '(main compilation target)' ,
            cwd         = os.getcwd()                 ,
            path        = targetPath                  ,
            libraryPath = options.libraryPath         ,
        )]
        
        allNames  = set()
        allFns    = {}
        
        macroContext = MacroContext()
        
        namedMacroExpansions = []
        
        uniques = Uniques()
        
        scanner = Scanner()
        
        while pending:
            
            pp = pending.pop()
            
            with self._context.where( "WHILE PROCESSING FILE: %s" % repr( pp.path() ) ):
                
                incode = pp.read_source()
                
                characters = Source( scanner.parse_characters(
                    data       = incode ,
                    fileSource = pp     ,
                ))
                
                tokens = Source( scanner.parse_tokens(
                    characters = characters
                ))
                
                definitions = Source( self._parser.parse_definitions(
                    tokens        = tokens       ,
                    currentModule = pp           ,
                    macroContext  = macroContext ,
                    uniques       = uniques      ,
                ))
                
                while True:
                    definition = definitions.take()
                    if not definition:
                        break
                    
                    elif definition.definition_type() == 'function':
                        # functions have to be recursively
                        # added because they have lambdas
                        # in them
                        
                        fns = [ definition ]
                        while fns:
                            fn = fns.pop(0)
                            if fn.name().value() in allNames:
                                raise Exception( 'duplicate function/macro name: %s' % repr( definition.name() ) )
                            else:
                                allNames.add( fn.name().value() )
                                allFns[ fn.name().value() ] = fn
                                
                                for subfn in fn.body().subfns():
                                    fns.append( subfn )
                    
                    elif definition.definition_type() == 'include':
                        # includes can be specified all over
                        # we just discard all repeat references
                        
                        norm = os.path.normpath( definition.path() )
                        if norm not in seen:
                            pending.append( definition )
                            seen.add( norm )
                        
                    elif definition.definition_type() == 'macro-definition':
                        
                        if definition.name().value() in allNames:
                            raise Exception( 'duplicate function/macro name: %s' % repr( definition.name() ) )
                        else:
                            allNames.add( definition.name().value() )
                            macroContext.add_macro( definition.name().value(), definition )
                        
                    elif definition.definition_type() == 'named-macro-expansion':
                        namedMacroExpansions.append( definition )
                        
                    else:
                        raise Exception( 'unknown definition type: %s' % repr( definition ) )
        
        if namedMacroExpansions:
            macroFunctions = self._parser.expand_macros(
                namedMacroExpansions = namedMacroExpansions ,
                macroContext         = macroContext         ,
                uniques              = uniques              ,
            )
            fns = []
            for mfn in macroFunctions:
                fns.append( mfn )
            while fns:
                fn = fns.pop(0)
                if fn.name().value() in allFns:
                    raise Exception(
                        'macro-generated function-name already defined: %s' % repr( fn.name().value() )
                    )
                else:
                    allNames.add( fn.name().value() )
                    allFns[ fn.name().value() ] = fn
                    for subfn in fn.body().subfns():
                        fns.append( subfn )
        
        callgraph, usedFns = self.analyze_functions( allFns, startname = self._options.startname )
        
        if options.optimize:
            outFns = optimize( allFns, usedFns, callgraph, self._options.startname, uniques )
            # drop functions we optimized out
            callgraph, usedFns = self.analyze_functions( outFns, startname = self._options.startname )
        else:
            outFns = allFns
        
        return outFns, usedFns

    # ensures all required functions are defined
    # returns list of all actually used functions
    # 
    # TODO: use a tree starting from _start so we only get what we really actually need
    # this includes anything that's in any function ( because we just modified a scanner )
    # 
    def analyze_functions(
        self      ,
        allFns    ,
        startname ,
    ):
        
        callgraph = {}
        
        # scan everything and build a graph of what functions reference each other
        # 
        for fn, dd in allFns.items():
            if fn not in callgraph:
                callgraph[ fn ] = set()
            for cc in dd.body().commands():
                if cc.kind() == 'word':
                    if (cc.value()) not in allFns:
                        raise Exception( 'unknown function called at %s in %s: %s' % (
                            cc.location() ,
                            repr( dd )    ,
                            repr( unmangle( cc.value() ) ),
                        ))
                    else:
                        callgraph[ fn ].add( cc.value() )
                elif cc.kind() == 'string':
                    pass
                elif cc.kind() == 'code':
                    pass
                elif cc.kind() == 'integer':
                    pass
                elif cc.kind() == 'localfn':
                    pass
                elif cc.kind() == 'FORWARDJUMPIF':
                    pass
                elif cc.kind() == 'JUMPTARGET':
                    pass
                elif cc.kind() == 'fnref':
                    if cc.value() not in allFns:
                        raise Exception( 'address of unknown function taken in %s: %s' % ( repr( dd ), repr( cc ) ) )
                    else:
                        callgraph[ fn ].add( cc.value() )
                elif cc.kind() == 'subfn':
                    if cc.value() not in allFns:
                        raise Exception( 'missing lambda in %s: %s' % ( repr( dd ), repr( cc ) ) )
                    else:
                        callgraph[ fn ].add( cc.value() )
                else:
                    raise Exception( 'unexpected command form: %s' % repr( cc ) )
        
        # they have to define a :_start function
        # by default, it's in the library/STANDARD
        # and calls :main after initialization
        # 
        if startname not in allFns:
            raise Exception( 'no %s function ( forget to @ "STANDARD" ; ? )' % repr( unmangle( startname ) ) )
        
        # walk from :_start down and figure out what
        # functions are actually used in the current
        # program
        # 
        usedFns = set()
        pending = [ startname ]
        while pending:
            pp = pending.pop()
            if pp in usedFns:
                continue
            else:
                usedFns.add( pp )
                for callee in callgraph[ pp ]:
                    pending.append( callee )
        
        return callgraph, usedFns
