
from modules.macro_list import MacroList

class ExpanderMacroList:
    def __init__(
        self          ,
        parameterList ,
    ):
        self._parameterList = parameterList
        return
    
    def consumes_argument( self ):
        return True
    
    def argument_consuming_variations( self, value ):
        
        if value.kind() != 'macrolist':
            raise Exception( 'cannot deconstruct a non-macrolist: %s' % repr( value ) )
        
        bits = value.bits()
        
        if len( bits ) == 0:
            yield MacroList(
                location = value.location() ,
                bits     = []               ,
            )
            return
        
        if len( bits ) != len( self._parameterList ):
            raise Exception( 'expected macrolist to have %s entries: %s' % (
                len( self._parameterList ) ,
                repr( value )              ,
            ))
        
        mapping = []
        index   = 0
        for parameter in self._parameterList:
            if parameter.consumes_argument():
                mapping.append(
                    (lambda which: lambda: parameter.expander().argument_consuming_variations( bits[which] ))( index )
                )
                index += 1
            else:
                mapping.append(
                    lambda: parameter.expander().non_argument_consuming_variations()
                )
        
        root  = mapping[0]()
        first = next( root, None )
        if first == None:
            return
        
        walk = [ [root,first] ]
        
        while True:
            
            # add additional items to fill out the structure
            # 
            while len( walk ) < len( bits ):
                ii = len( walk )
                ss = mapping[ii]()
                vv = next( ss, None )
                if vv == None:
                    break
                else:
                    walk.append( [ss,vv] )
            
            # if we filled a tuple, pass it out
            if len( walk ) == len( bits ):
                mm = MacroList(
                    location = value.location()               ,
                    bits     = list( bb for (aa,bb) in walk ) ,
                )
                yield mm
            
            # update the rearmost item
            # remove it if it returns none
            # repeat.
            # 
            while walk:
                vv = next( walk[-1][0], None )
                if vv == None:
                    walk.pop()
                    continue
                else:
                    walk[-1][1] = vv
                    break
            
            # stop if the initial variation returned none and was therefore removed
            if not walk:
                break
        
        return
