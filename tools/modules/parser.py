
import re

from modules.filesource                     import FileSource
from modules.source                         import Source
from modules.mangling                       import mangle, unmangle
from modules.token                          import Token
from modules.body                           import Body
from modules.named_function                 import NamedFunction
from modules.expander_scalar                import ExpanderScalar
from modules.macro_parameter                import MacroParameter
from modules.namer_scalar                   import NamerScalar
from modules.expansion_rule_each            import ExpansionRuleEach
from modules.expansion_rule_count           import ExpansionRuleCount
from modules.expansion_rule_first           import ExpansionRuleFirst
from modules.expansion_rule_rest            import ExpansionRuleRest
from modules.expansion_rule_to_zero         import ExpansionRuleToZero
from modules.expansion_rule_to_one          import ExpansionRuleToOne
from modules.expansion_rule_decr            import ExpansionRuleDecr
from modules.expansion_rule_incr            import ExpansionRuleIncr
from modules.expansion_rule_if              import ExpansionRuleIf
from modules.expansion_rule_not             import ExpansionRuleNot
from modules.expansion_rule_is_empty        import ExpansionRuleIsEmpty
from modules.expansion_rule_is_equal        import ExpansionRuleIsEqual
from modules.expansion_rule_is_less_than    import ExpansionRuleIsLessThan
from modules.expansion_rule_is_greater_than import ExpansionRuleIsGreaterThan
from modules.expansion_rule_collect         import ExpansionRuleCollect
from modules.expansion_rule_length          import ExpansionRuleLength
from modules.expansion_rule_sort            import ExpansionRuleSort
from modules.expansion_rule_reverse         import ExpansionRuleReverse
from modules.expansion_rule_string          import ExpansionRuleString
from modules.expansion_rule_expandno        import ExpansionRuleExpandNo
from modules.expansion_rule_globalno        import ExpansionRuleGlobalNo
from modules.unexpanded_macro_expansion     import UnexpandedMacroExpansion
from modules.macro_definition               import MacroDefinition
from modules.named_macro_expansion          import NamedMacroExpansion
from modules.lambda_function                import LambdaFunction
from modules.namer_macro_list               import NamerMacroList
from modules.expander_macro_list            import ExpanderMacroList
from modules.unexpanded_function_definition import UnexpandedFunctionDefinition
from modules.macro_list                     import MacroList
from modules.named_arg_source               import NamedArgSource
from modules.variations                     import Variations
from modules.named_non_arg_source           import NamedNonArgSource

class Parser:
    
    def __init__(
        self    ,
        options ,
        context ,
    ):
        self._options = options
        self._context = context
        return
    
    def parse_definitions(
        self          ,
        tokens        ,
        currentModule ,
        macroContext  ,
        uniques       ,
    ):
        while True:
            initial = tokens.take()
            if not initial:
                return
            elif initial.kind() == ':':
                yield self.parse_named_function(
                    initial       = initial       ,
                    tokens        = tokens        ,
                    currentModule = currentModule ,
                    macroContext  = macroContext  ,
                    uniques       = uniques       ,
                )
            elif initial.kind() == '@':
                pp = tokens.peek()
                if pp and pp.kind() == 'string':
                    yield self.parse_include(
                        initial       = initial       ,
                        tokens        = tokens        ,
                        currentModule = currentModule ,
                    )
                else:
                    yield self.parse_named_macro_expansion(
                        initial       = initial       ,
                        tokens        = tokens        ,
                        currentModule = currentModule ,
                        macroContext  = macroContext  ,
                        uniques       = uniques       ,
                    )
            elif initial.kind() == 'word' and initial.value() == '%':
                yield self.parse_macro_definition(
                    initial       = initial       ,
                    tokens        = tokens        ,
                    currentModule = currentModule ,
                )
            else:
                raise Exception(
                    'unknown definition marker: %s' % repr( initial )
                )

    def parse_named_function(
        self          ,
        initial       ,
        tokens        ,
        currentModule ,
        macroContext  ,
        uniques       ,
    ):
        name = tokens.take()
        if not name:
            raise Exception(
                'expected name of definition after %s, found end of data' % repr( initial )
            )
        if name.kind() == 'word':
            pass
        else:
            raise Exception(
                'expected name of definition after %s, found: %s' % (
                    repr( initial ) ,
                    repr( name )    ,
                )
            )
        
        with self._context.where( "WHILE PROCESSING FUNCTION: %s" % repr( name ) ):
            bodyBits = self.capture_balanced_bits_til_terminator( tokens )
            
            end = tokens.take()
            if end == None:
                raise Exception( 'expected ";" after %s' % repr( initial ) )
            elif end.kind() != ';':
                raise Exception(
                    'expected ";" after %s, found %s' % ( repr( initial ), repr( end ) )
                )
            
            bodyBits.append( end )
            
            body = self.parse_body(
                initial = initial,
                tokens  = Source( self.expand_bitstream(
                    macroContext = macroContext       ,
                    tokens       = Source( bodyBits ) ,
                    uniques      = uniques            ,
                )),
                parent  = mangle(':' + name.value()),
                uniques = uniques,
            )
        
        return NamedFunction(
            location = initial.location() ,
            name     = name               ,
            body     = body               ,
        )
    
    def parse_lambda_definition(
        self    ,
        initial ,
        tokens  ,
        parent  ,
        uniques ,
    ):
        name = 'kmlambda_%s' % str(uniques.get())
        body = self.parse_body(
            initial ,
            tokens  ,
            name    ,
            uniques ,
        )
        return LambdaFunction(
            location   = initial.location() ,
            lambdaName = name               ,
            body       = body               ,
            parent     = parent             ,
        )
    
    def parse_body(
        self    ,
        initial ,
        tokens  ,
        parent  ,
        uniques ,
    ):
        # { args -- locals }
        # args are just locals that automatically set
        # 
        localargs, localvars = self.parse_optional_locals( tokens )
        
        commands = []
        
        # here we insert (in reverse order so right sets first )
        # localfns for all of the args the function defined
        # 
        for arg in reversed( localargs ):
            commands.append( Token(
                location = arg.location(),
                kind     = 'localfn',
                value    = arg.value() + '.set'
            ))
        
        subfns   = []
        while True:
            pt = tokens.peek()
            if not pt:
                break
            elif pt.kind() == ';':
                break
            elif pt.kind() == ']':
                break
            elif pt.kind() == '[':
                tokens.take()
                subfntoks = []
                depth = []
                while True:
                    st = tokens.take()
                    if st == None:
                        if len(depth):
                            raise Exception( 'unclosed %s at %s' % (repr(depth[-1].kind()), depth[-1].location()) )
                        else:
                            raise Exception( 'unclosed %s at %s' % (repr(pt.kind()), pt.location()))
                    elif st.kind() in ']}':
                        if st.kind() == ']' and len(depth) == 0:
                            break
                        elif depth[-1].kind() == '[':
                            depth.pop()
                            subfntoks.append( st )
                        elif depth[-1].kind() == '{':
                            depth.pop()
                            subfntoks.append( st )
                        else:
                            raise Exception( 'unexpected "]" does not line up with a matching "[" at %s' % pt.location() )
                    elif st.kind() == '[':
                        depth.append(st)
                        subfntoks.append( st )
                    elif st.kind() == '{':
                        depth.append(st)
                        subfntoks.append( st )
                    else:
                        subfntoks.append( st )
                subfn = self.parse_lambda_definition(
                    initial = pt                  ,
                    tokens  = Source( subfntoks ) ,
                    parent  = parent              ,
                    uniques = uniques             ,
                )
                subfns.append( subfn )
                commands.append( Token(
                    location = subfn.location()     ,
                    kind     = 'subfn'              ,
                    value    = subfn.name().value() ,
                ))
            
            elif pt.kind() == 'word':
                tokens.take()
                commands.append( Token(
                    location = pt.location()              ,
                    kind     = 'word'                     ,
                    value    = mangle( ':' + pt.value() ) ,
                ))
            elif pt.kind() == 'fnref':
                tokens.take()
                commands.append( Token(
                    location = pt.location()              ,
                    kind     = 'fnref'                    ,
                    value    = mangle( ':' + pt.value() ) ,
                ))
            elif pt.kind() in [ 'localfn', 'string', 'integer', 'code' ]:
                tokens.take()
                commands.append( pt )
                
            elif pt.kind() in ['(', 'macrolist']:
                raise Exception( 'macrolist outside of macro-parameters or arguments: %s' % repr( pt ) )
            
            else:
                raise Exception( 'what is %s' % repr( pt ) )
        
        return Body(
            location  = initial.location() ,
            commands  = commands           ,
            localargs = localargs          ,
            localvars = localvars          ,
            subfns    = subfns             ,
        )
    
    def parse_optional_locals(
        self   ,
        tokens ,
    ):
        pt = tokens.peek()
        if not pt:
            return [],[]
        elif pt.kind() != '{':
            return [],[]
        else:
            tokens.take()
        
        seen      = set()
        localArgs = []
        localVars = []
        
        dividerSeen = False
        
        while True:
            pt = tokens.peek()
            if pt == None:
                break
            elif pt.kind() == 'word' and pt.value() == '--':
                if dividerSeen:
                    raise Exception( 'extra divider in function variable specification: %s' % repr( pt ) )
                else:
                    tokens.take()
                    dividerSeen = True
            elif pt.kind() != 'localfn':
                break
            else:
                tokens.take()
                
                vv = pt.value()
                sz = 8
                if '.' in vv:
                    fore, aft = vv.split('.',1)
                    if not (fore[1:] and fore[1:].isdigit()):
                        raise Exception(
                            'localfn size designation must be a number ($<size>.<name>), found %s' % pt
                        )
                    else:
                        vv = '$' + aft
                        sz = int(fore[1:], 10)
                        if sz < 1:
                            raise Exception( 'localfn size designation must be an integer of 1 or greater' )
                        if sz % 8 != 0:
                            sz += 8 - sz % 8
                
                if '.' in vv:
                    raise Exception( 'localfn name cannot contain "." (must be $<size>.<name> or $<name>)' )
                
                if vv in seen:
                    raise Exception( 'duplicate localfn name declaration: %s' % repr( pt ) )
                elif dividerSeen:
                    seen.add( vv )
                    localVars.append( (vv,sz) )
                else:
                    if sz != 8:
                        raise Exception( 'local args can only be size 8, found: %s' % repr( pt ) )
                    seen.add( vv )
                    localArgs.append( pt )
                    localVars.append( (vv,sz) )
        
        ct = tokens.take()
        if not ct:
            raise Exception( 'expected } following: %s' % repr( pt ) )
        elif ct.kind() != '}':
            raise Exception( 'expected } following %s, found %s' % ( repr( pt ), repr( ct ) ) )
        
        return localArgs, localVars

    def parse_include(
        self          ,
        initial       ,
        tokens        ,
        currentModule ,
    ):
        path = tokens.take()
        if path == None:
            raise Exception( 'found nothing while expecting path after: %s' % repr( initial ) )
        
        if path.kind() != 'string':
            raise Exception( 'expected path after @, found %s' % repr( path ) )
        
        end = tokens.take()
        if end == None:
            raise Exception( 'found nothing while expecting ";" after: %s' % repr( path ) )
        
        if end.kind() != ';':
            raise Exception( 'expected ; after path, found %s' % repr( end ) )
        
        return FileSource(
            origin      = '(included from file=%s)' % currentModule.path() ,
            cwd         = currentModule.cwd_for_includes()                 ,
            path        = path.value()                                     ,
            libraryPath = currentModule.library_path()                     ,
        )
    
    def parse_macro_definition(
        self          ,
        initial       ,
        tokens        ,
        currentModule ,
    ):
        # % name ( parameters ) 
        #     : function definition
        #       we should not expand yet
        #       just collect the contents
        #     ;
        #     @ named/macro/expansion
        #       and vars we should also collect
        #       for later expansion when the
        #       containing macro is expanded
        #     ;
        #     ...repeat...
        # ;
        
        name = tokens.take()
        if not name:
            raise Exception( 'expected name after macro definition sigil: %s' % repr( initial ) )
        elif name.kind() != 'word':
            raise Exception( 'expected name after macro definition sigil to be word, found: %s' % repr( name ) )
        
        parameters = self.parse_macro_parameter_list(
            initial = initial ,
            tokens  = tokens  ,
        )
        
        unexpandedDefinitions = self.parse_unexpanded_definitions(
            tokens        = tokens        ,
            currentModule = currentModule ,
        )
        
        closer = tokens.take()
        if not closer:
            raise Exception( 'expected ";" to terminate macro definition starting at: %s' % repr( initial ) )
        elif closer.kind() != ';':
            raise Exception( 'expected ";" to terminate macro definition starting at %s, instead found: %s' % (
                repr( initial ) ,
                repr( closer  ) ,
            ))
        
        return MacroDefinition(
            name                  = name                  ,
            parameters            = parameters            ,
            unexpandedDefinitions = unexpandedDefinitions ,
        )

    def parse_macro_parameter_list(
        self                ,
        initial             , # macro initial character
        tokens              ,
    ):
        start = tokens.take()
        if not start:
            raise Exception( 'expected "(" to start macro parameters in macro starting at: %s' % repr( initial ) )
        elif start.kind() != '(':
            raise Exception( 'expected "(" to start macro parameters in macro starting at %s, instead found: %s' % (
                repr( initial ),
                repr( start   ),
            ))
        
        parameters = self.parse_macro_parameters(
            initial = initial ,
            tokens  = tokens  ,
        )
        
        closer = tokens.take()
        if not closer:
            raise Exception( 'expected ")" to close macro parameters in macro starting at: %s' % repr( initial ) )
        elif closer.kind() != ')':
            raise Exception( 'expected ")" to close macro parameters in macro starting at: %s, found: %s' % (
                repr( initial ),
                repr( closer  ),
            ))
        
        return parameters
    
    def parse_macro_parameters(
        self    ,
        initial ,
        tokens  ,
    ):
        parameters = []
        while True:
            parameter = self.parse_macro_parameter(
                initial = initial ,
                tokens  = tokens  ,
            )
            if parameter == None:
                break
            
            parameters.append( parameter )
        
        return parameters
    
    def parse_macro_parameter(
        self    ,
        initial ,
        tokens  ,
    ):
        name = tokens.peek()
        if not name:
            return
        elif name.kind() == ')':
            return
        elif name.kind() not in [ 'macrovar', '(' ]:
            raise Exception( 'expected a macrovar in macro parameters of macro definition at %s, found: %s' % (
                repr( initial ) ,
                repr( name    ) ,
            ))
        
        if name.kind() == '(':
            with self._context.where( 'while parsing macro parameters starting at %s' % repr( initial ) ):
                parameterList = self.parse_macro_parameter_list(
                    initial = initial ,
                    tokens  = tokens  ,
                )
                
                return MacroParameter(
                    initial  = name ,
                    namer    = NamerMacroList(
                        parameterList = parameterList ,
                    ),
                    expander = ExpanderMacroList(
                        parameterList = parameterList ,
                    ),
                )
            
            raise Exception( 'there it is' )
        
        tokens.take()
        
        bits = name.value().split(".")
        
        expander = ExpanderScalar(
            context = self._context,
        )
        
        parameter = MacroParameter(
            initial  = name                          ,
            namer    = NamerScalar( name = bits[0] ) ,
            expander = expander                      ,
        )
        
        expansionRules = {
            'each'          : ExpansionRuleEach          ,
            'count'         : ExpansionRuleCount         ,
            'first'         : ExpansionRuleFirst         ,
            'rest'          : ExpansionRuleRest          ,
            'toZero'        : ExpansionRuleToZero        ,
            'toOne'         : ExpansionRuleToOne         ,
            'decr'          : ExpansionRuleDecr          ,
            'incr'          : ExpansionRuleIncr          ,
            'if'            : ExpansionRuleIf            ,
            'not'           : ExpansionRuleNot           ,
            'isEmpty'       : ExpansionRuleIsEmpty       ,
            'isEqual'       : ExpansionRuleIsEqual       ,
            'isLessThan'    : ExpansionRuleIsLessThan    ,
            'isGreaterThan' : ExpansionRuleIsGreaterThan ,
            'collect'       : ExpansionRuleCollect       ,
            'length'        : ExpansionRuleLength        ,
            'sort'          : ExpansionRuleSort          ,
            'reverse'       : ExpansionRuleReverse       ,
            'string'        : ExpansionRuleString        ,
            
            'expandno'      : ExpansionRuleExpandNo      ,
            'globalno'      : ExpansionRuleGlobalNo      ,
        }
        
        for bit in bits[1:]:
            if bit in expansionRules:
                expander.add_expansion_rule( expansionRules[ bit ], location = name.location() )
            else:
                raise Exception( 'unknown expansion rule: %s' % repr( bit ) )
        
        return parameter

    def parse_unexpanded_definitions(
        self          ,
        tokens        ,
        currentModule ,
    ):
        unexpandedDefinitions = []
        while True:
            unexpandedDefinition = self.parse_unexpanded_definition(
                tokens        = tokens        ,
                currentModule = currentModule ,
            )
            if not unexpandedDefinition:
                break
            else:
                unexpandedDefinitions.append( unexpandedDefinition )
        return unexpandedDefinitions
    
    def parse_unexpanded_definition(
        self          ,
        tokens        ,
        currentModule ,
    ):
        start = tokens.peek()
        if not start:
            return
        elif start.kind() == ';':
            return
        elif not ( start.kind() == ':' or start.kind() == '@' ):
            raise Exception(
                'expected ":" or "@" to start definition expansions, instead found: %s' % repr( start )
            )
        
        tokens.take()
        
        with self._context.where( 'while scanning in unexpanded definition starting at %s' % repr( start ) ):
            bits = self.capture_balanced_bits_til_terminator( tokens )
        
        end = tokens.take()
        if not end:
            raise Exception( 'missing expected ";" to terminate statement starting with: %s' % repr( start ) )
        elif end.kind() != ';':
            raise Exception( 'missing expected ";" to terminate statement starting with %s, instead found: %s' % (
                repr( start ) ,
                repr( end   ) ,
            ))
        
        bits.append( end )
        
        if start.kind() == ':':
            return UnexpandedFunctionDefinition(
                initial       = start         ,
                bits          = bits          ,
                currentModule = currentModule ,
            )
        elif start.kind() == '@':
            return UnexpandedMacroExpansion(
                initial       = start         ,
                bits          = bits          ,
                currentModule = currentModule ,
            )
        else:
            raise Exception( 'not sure what this is: %s' % repr( start ) )
    
    def capture_balanced_bits_til_terminator(
        self   ,
        tokens ,
    ):
        depthStack = []
        bits = []
        while True:
            bit = tokens.peek()
            if bit == None:
                raise Exception(
                    'ran out of tokens while collecting statement: firstbit=%s' % repr( (bits and bits[0]) or None )
                )
            
            if bit.kind() in [ '[', '{', '(' ]:
                tokens.take()
                bits.append( bit )
                depthStack.append( bit )
            elif bit.kind() in [ ']', '}', ')' ]:
                if depthStack:
                    tokens.take()
                    bits.append( bit )
                    matches = { '[' : ']', '{' : '}', '(' : ')' }
                    if matches[ depthStack[-1].kind() ] == bit.kind():
                        depthStack.pop()
                    else:
                        raise Exception( 'expected "%s" to match %s, instead found: %s' % (
                            matches[ depthStack[-1].kind() ] == bit.kind() ,
                            repr( depthStack[-1] )                         ,
                            repr( bit )                                    ,
                        ))
                else:
                    # do not take!
                    break
            elif bit.kind() == ';':
                if depthStack:
                    raise Exception( 'unterminated "%s" starting at: %s' % (
                        depthStack[-1].kind()  ,
                        repr( depthStack[-1] ) ,
                    ))
                else:
                    # do not take!
                    break
            else:
                tokens.take()
                bits.append( bit )
                pass
        
        return bits

    def parse_named_macro_expansion(
        self          ,
        initial       ,
        tokens        ,
        currentModule ,
        macroContext  ,
        uniques       ,
    ):
        # not expanding it yet, just recording the invocation so we can expand it later
        # the @ is in initial
        # 
        #   @ macro-name macro arguments (can be lists) [ or lamdbas ] ;
        # 
        
        name = tokens.take()
        if not name:
            raise Exception( 'expected name of macro to expand to follow macro expansion sigil at: %s' % repr( initial ) )
        elif name.kind() != 'word':
            raise Exception( 'expected name of macro to expand to follow macro expansion sigil at %s, instead found: %s' % (
                repr( initial ) ,
                repr( name    ) ,
            ))
        
        with self._context.where(
            'while scanning for named macro expansion arguments for expansion starting at: %s' % (
                repr( initial )
            )
        ):
            argumentBits = self.capture_balanced_bits_til_terminator(
                tokens ,
            )
            
            argumentBitsSource = Source( argumentBits )
            
            expandedArgumentBits = self.expand_bitstream(
                macroContext = macroContext      ,
                tokens      = argumentBitsSource ,
                uniques     = uniques            ,
            )
            
            expandedArgumentBitsSource = Source( expandedArgumentBits )
            
            arguments = self.parse_macro_expansion_arguments(
                initial = initial                    ,
                tokens  = expandedArgumentBitsSource ,
            )
        
        closer = tokens.take()
        if not closer:
            raise Exception( 'expected ";" to close macro expansion at: %s' % repr( initial ) )
        elif closer.kind() != ';':
            raise Exception( 'expected ";" to close macro expansion at: %s, instead found: %s' % (
                repr( initial ) ,
                repr( closer  ) ,
            ))
        
        return NamedMacroExpansion(
            initial   = initial   ,
            macroName = name      ,
            arguments = arguments ,
        )

    def parse_macro_expansion_arguments(
        self    ,
        initial ,
        tokens  ,
    ):
        arguments = []
        
        while True:
            argument = self.parse_macro_expansion_argument(
                initial = initial ,
                tokens  = tokens  ,
            )
            if not argument:
                break
            else:
                arguments.append( argument )
        
        return arguments
    
    def parse_macro_expansion_argument(
        self    ,
        initial ,
        tokens  ,
    ):
        # name
        # @name 
        # number
        # "string"
        # [ all of the above ]
        # ( all of the above )
        
        pp = tokens.peek()
        if pp == None:
            return
        elif pp.kind() == ';':
            return
        elif pp.kind() in [ ')', ']' ]:
            return
        
        tokens.take()
        
        if pp.kind() in [ 'word', 'macrovar', 'integer', 'string', 'macrolist' ]:
            return pp
        
        elif pp.kind() == '[':
            bits = self.parse_macro_expansion_arguments(
                initial ,
                tokens  ,
            )
            
            closer = tokens.take()
            if not closer:
                raise Exception( 'unterminated lambda statement starting at: %s' % repr( pp ) )
            elif closer.kind() != ']':
                raise Exception( 'expected "]" to close lambda at %s, instead found: %s' % (
                    repr( pp     ) ,
                    repr( closer ) ,
                ))
            
            return ExpandableLambda( pp, bits )
        
        elif pp.kind() == '(':
            bits = self.parse_macro_expansion_arguments(
                initial ,
                tokens  ,
            )
            
            closer = tokens.take()
            if not closer:
                raise Exception( 'unterminated macro-list starting at: %s' % repr( pp ) )
            elif closer.kind() != ')':
                raise Exception( 'expected ")" to close macro-list at %s, instead found: %s' % (
                    repr( pp     ) ,
                    repr( closer ) ,
                ))
            
            return MacroList(
                location = pp.location() ,
                bits     = bits          ,
            )
        else:
            raise Exception( 'unknown bit in macro expansion variables: %s' % repr( pp ) )

    def expand_bitstream(
        self         ,
        macroContext ,
        tokens       ,
        uniques      ,
    ):
        while True:
            bit = tokens.take()
            if not bit:
                break
            elif bit.kind() == 'macrovar':
                yield macroContext.expand_macrovar( bit )
            elif bit.kind() == '@':
                if self._options.showExpansions:
                    EXPANSIONID = self._context.next_expansion_id()
                    EXPANDED = []
                else:
                    EXPANSIONID = 'NOT-EXPANDING'
                for bit in self.extract_and_expand_local_macro(
                    macroContext = macroContext ,
                    tokens       = tokens       ,
                    expansionId  = EXPANSIONID  ,
                    uniques      = uniques      ,
                ):
                    if self._options.showExpansions:
                        EXPANDED.append( bit )
                    yield bit
                if self._options.showExpansions:
                    self._context.log( 'EXPANDED-LOCAL', 'XID=', EXPANSIONID, 'TO', repr(' '.join([ E.simple() for E in EXPANDED ])) )
            elif bit.kind() == 'macrostring':
                yield self.expand_macrostring(
                    macroContext = macroContext ,
                    macroString  = bit          ,
                )
            elif bit.kind() == 'macrocode':
                yield self.expand_macrocode(
                    macroContext = macroContext ,
                    macroCode    = bit          ,
                )
            elif bit.kind() == 'macrolist':
                yield MacroList(
                    location = bit.location()                 ,
                    bits     = list(self.expand_bitstream(
                        macroContext = macroContext ,
                        tokens       = Source( bit.bits() ) ,
                        uniques      = uniques ,
                    )),
                )
            elif bit.kind() in [ ';', '{', '}', '[', ']', '(', ')', 'localfn', 'word', 'integer', 'string', 'code', 'fnref' ]:
                yield bit
            else:
                raise Exception( 'unknown bit in macro expansion bitstream: %s' % repr( bit ) )

    def expand_macros(
        self                 ,
        namedMacroExpansions ,
        macroContext         ,
        uniques              ,
    ):
        for macroExpansion in namedMacroExpansions:
            fns = self.expand_macro(
                macroExpansion = macroExpansion ,
                macroContext   = macroContext   ,
                uniques        = uniques        ,
            )
            for fn in fns:
                yield fn
        
    def expand_macro(
        self           ,
        macroExpansion ,
        macroContext   ,
        uniques        ,
    ):
        if self._options.showExpansions:
            self._context.log( 'EXPANDING-NAMED', macroExpansion.simple() )
        
        if not macroContext.has_macro( macroExpansion.macro_name().value() ):
            raise Exception( 'unknown macro definition: %s' % macroExpansion.macro_name() )
        
        md = macroContext.get_macro( macroExpansion.macro_name().value() )
        
        expansions = self.determine_macro_expansions(
            macroStart = macroExpansion.initial()           ,
            parameters = md.parameters()                    ,
            arguments  = list( macroExpansion.arguments() ) ,
        )
        
        expandedFunctions = []
        for group in expansions:
            
            expansionContext = macroContext.copy()
            
            for (name, value) in group:
                expansionContext.add_macrovar( name, value )
            
            for unexpandedDefinition in md.unexpanded_definitions():
                
                if unexpandedDefinition.initial().kind() == ':':
                    expandedBits = self.expand_bitstream(
                        macroContext = expansionContext                      ,
                        tokens       = Source( unexpandedDefinition.bits() ) ,
                        uniques      = uniques                               ,
                    )
                    expandedFunction = self.parse_named_function(
                        initial       = unexpandedDefinition.initial()        ,
                        tokens        = Source( expandedBits )                ,
                        currentModule = unexpandedDefinition.current_module() ,
                        macroContext  = macroContext                          ,
                        uniques       = uniques                               ,
                    )
                    expandedFunctions.append( expandedFunction )
                    if self._options.showExpansions:
                        self._context.log( 'EXPANDED-FUNCTION', expandedFunction.simple() )
                    
                elif unexpandedDefinition.initial().kind() == '@': # or macrovar?
                    
                    expandedBits = self.expand_bitstream(
                        macroContext = expansionContext                      ,
                        tokens       = Source( unexpandedDefinition.bits() ) ,
                        uniques      = uniques                               ,
                    )
                    expandedExpansion = self.parse_named_macro_expansion(
                        initial       = unexpandedDefinition.initial()        ,
                        tokens        = Source( expandedBits )                ,
                        currentModule = unexpandedDefinition.current_module() ,
                        macroContext  = macroContext                          ,
                        uniques       = uniques                               ,
                    )
                    for fn in self.expand_macro(
                        macroExpansion = expandedExpansion ,
                        macroContext   = macroContext      ,
                        uniques        = uniques           ,
                    ):
                        expandedFunctions.append( fn )
                    
                else:
                    raise Exception(
                        'unknown unexpanded definition type in macro expansion: %s' % (
                            repr( unexpandedDefinition.initial() ) ,
                        )
                    )
        
        return expandedFunctions
    
    def determine_macro_expansions(
        self       ,
        macroStart ,
        parameters ,
        arguments  ,
    ):
        argSource = Source( arguments )
        
        nArgParams = sum( 1 for param in parameters if param.consumes_argument() )
        nArgs      = len( arguments )
        if nArgParams != nArgs:
            raise Exception(
                'macro expansion has %s argument consuming parameters, but received %s arguments at %s' % (
                    repr( nArgParams ) ,
                    repr( nArgs      ) ,
                    repr( macroStart ) ,
                )
            )
        
        expansionArgSources = []
        for param in parameters:
            if param.consumes_argument():
                arg = argSource.take()
                if arg == None:
                    raise Exception(
                        'expansion at %s lacks argument for macro parameter: %s' % (
                            repr( macroStart ) ,
                            param.name()       ,
                        )
                    )
                else:
                    expansionArgSources.append( NamedArgSource(
                        namer    = param.namer()    ,
                        expander = param.expander() ,
                        source   = arg              ,
                    ))
            else:
                expansionArgSources.append( NamedNonArgSource(
                    namer    = param.namer()    ,
                    expander = param.expander() ,
                ))
        
        return self.chain_argument_sources( expansionArgSources )
    
    def chain_argument_sources(
        self           ,
        sources        ,
        _left   = None ,
    ):
        _left = _left or ()
        if self._options.showExpansions:
            self._context.log('LEFT=%s' % repr(_left))
        if sources:
            source, remaining = sources[0], sources[1:]
            if self._options.showExpansions:
                self._context.log('CHAINING %s TO %s' % (repr(source), repr(remaining)))
            for vv in source.variations():
                if remaining:
                    for group in self.chain_argument_sources( remaining, _left + tuple( source.namer().names( vv ) ) ):
                        yield group
                else:
                    chained = _left + tuple( source.namer().names( vv ) )
                    if self._options.showExpansions:
                        self._context.log( 'CHAINED', chained )
                    yield chained
        else:
            yield _left

    def extract_and_expand_local_macro(
        self         ,
        macroContext ,
        tokens       ,
        expansionId  ,
        uniques      ,
    ):
        # ( () () ... )
        # 
        #   argument expansion
        #   parameter interpretation
        #   body generation
        
        start = tokens.take()
        if not start:
            raise Exception( 'how did you even get here without a "(" ?' )
        elif start.kind() != '(':
            raise Exception( 'seriously, how without a "(" ?' )
        
        with self._context.where( 'while parsing macro starting at: %s' % repr( start ) ):
            arguments = self.extract_local_macro_arguments(
                macroContext = macroContext ,
                tokens       = tokens       ,
                uniques      = uniques      ,
            )
            
            parameters = self.parse_macro_parameter_list(
                initial = start  ,
                tokens  = tokens ,
            )
            
            bodyBits = list( self.capture_balanced_bits_til_terminator(
                tokens ,
            ))
            
            if self._options.showExpansions:
                self._context.log(
                    'EXPANDING-LOCAL', 'XID=', expansionId ,
                    'arguments='     , repr(' '.join([ A.simple() for A in arguments  ])) ,
                    'parameters='    , repr(' '.join([ P.simple() for P in parameters ])) ,
                    'bodyBits='      , repr(' '.join([ B.simple() for B in bodyBits   ])) ,
                )
            
            end = tokens.take()
            if not end:
                raise Exception( 'missing ")" for macro starting at %s' % repr( start ) )
            elif end.kind() != ')':
                raise Exception( 'expected ")" for macro starting at %s, instead found: %s' % (
                    repr( start ) ,
                    repr( end )   ,
                ))
            
            for group in self.determine_macro_expansions(
                macroStart = start      ,
                parameters = parameters ,
                arguments  = arguments  ,
            ):
                expansionContext = macroContext.copy()
                
                for (name, value) in group:
                    expansionContext.add_macrovar( name, value )
                
                bodyBitsSource = Source( bodyBits )
                
                expandedBody = self.expand_bitstream(
                    macroContext = expansionContext ,
                    tokens       = bodyBitsSource   ,
                    uniques      = uniques          ,
                )
                
                for bit in expandedBody:
                    yield bit
        
        return
    
    def extract_local_macro_arguments(
        self         ,
        macroContext ,
        tokens       ,
        uniques      ,
    ):
        start = tokens.take()
        if not start:
            raise Exception( 'expected "(" to begin local-macro argument section' )
        elif start.kind() != '(':
            raise Exception( 'expected "(" to begin local-macro argument section, instead found: %s' % repr( start ) )
        
        argumentBits = self.capture_balanced_bits_til_terminator(
            tokens ,
        )
        
        argumentBitsSource = Source( argumentBits )
        
        expandedArgumentBits = list( self.expand_bitstream(
            macroContext = macroContext       ,
            tokens       = argumentBitsSource ,
            uniques      = uniques            ,
        ))
        
        expandedArgumentBitsSource = Source( expandedArgumentBits )
        
        macroArguments = self.parse_macro_expansion_arguments(
            initial = start                      ,
            tokens  = expandedArgumentBitsSource ,
        )
        
        # after because source is lazy
        # we have to give it a chance to be consumed
        trash = argumentBitsSource.take()
        if trash:
            raise Exception( 'failed to expand: %s' % repr( trash ) )
        
        trash = expandedArgumentBitsSource.take()
        if trash:
            raise Exception( 'failed to parse all expanded bits: %s' % repr( trash ) )
        
        end = tokens.take()
        if not end:
            raise Exception( 'expected ")" to end arguments section starting at: %s' % repr( start ) )
        elif end.kind() != ')':
            raise Exception( 'expected ")" to end arguments section starting at %s, instead found: %s' % (
                repr( start ) ,
                repr( end   ) ,
            ))
        
        return macroArguments

    def expand_macrostring(
        self         ,
        macroContext ,
        macroString  ,
    ):
        if macroString.kind() != 'macrostring':
            raise Exception( 'impossible' )
        
        def replace( mm ):
            macrovar = mm.group('name')
            if macrovar == '@':
                return '@'
            if not macroContext.has_macrovar( macrovar ):
                raise Exception( 'while expanding macrostring (%s), missing macrovar: %s' % (
                    repr( macroString ) ,
                    repr( macrovar )    ,
                ))
            vv = macroContext.get_macrovar( macrovar )
            if vv.kind() == 'word':
                return vv.value()
            elif vv.kind() == 'integer':
                return str( vv.value() )
            elif vv.kind() == 'string':
                return vv.value()
            else:
                raise Exception( 'cannot interpolate macrostring (%s), macrovar (%s) is a %s' % (
                    repr( macroString ) ,
                    repr( macrovar )    ,
                    str( vv.kind() )    ,
                ))
        
        interpolated = re.sub( '(?P<name>[@][A-Za-z][A-Za-z0-9]*)[@]', replace, macroString.value() )
        
        return Token(
            location = macroString.location() ,
            kind     = 'string'               ,
            value    = interpolated           ,
        )
    
    def expand_macrocode(
        self         ,
        macroContext ,
        macroCode    ,
    ):
        if macroCode.kind() != 'macrocode':
            raise Exception( 'impossible' )
        
        def replace( mm ):
            macrovar = mm.group('name')
            if macrovar == '@':
                return ''
            if not macroContext.has_macrovar( macrovar ):
                raise Exception( 'while expanding macrocode (%s), missing macrovar: %s' % (
                    repr( macroCode ) ,
                    repr( macrovar )  ,
                ))
            vv = macroContext.get_macrovar( macrovar )
            if vv.kind() == 'word':
                return vv.value()
            elif vv.kind() == 'integer':
                return str( vv.value() )
            elif vv.kind() == 'string':
                return vv.value()
            else:
                raise Exception( 'cannot interpolate macrocode (%s), macrovar (%s) is a %s' % (
                    repr( macroString ) ,
                    repr( macrovar )    ,
                    str( vv.kind() )    ,
                ))
        
        interpolated = re.sub( '(?P<name>[@][A-Za-z][A-Za-z0-9]*)[@]', replace, macroCode.value() )
        
        return Token(
            location = macroCode.location() ,
            kind     = 'code'               ,
            value    = interpolated         ,
        )
