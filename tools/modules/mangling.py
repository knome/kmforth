
import binascii

import modules.constants as constants
from modules.source import Source

def mangle( name ):
    bits = []
    
    for cc in name:
        if cc.lower() in constants.LETTERS:
            bits.append( cc )
        elif cc in constants.NUMBERS:
            bits.append( cc )
        else:
            for byte in cc.encode( 'utf-8' ):
                bits.append( '_' + hex(byte)[2:] + '_' )
    
    final = 'kmfn_' + ''.join( bits )
    
    return final

def unmangle( name ):
    bits = []
    ss   = Source( name[len('kmfb_'):] )
    
    if name.startswith( 'kmlambda'):
        # lambdas aren't mangled and it is useful to
        # call this where lambdas and functions are combined
        return name
    
    while ss.peek() != None:
        vv = ss.take()
        if vv == '_':
            bits.append( ss.take() + ss.take() )
            ss.take()
        else:
            bits.append( ''.join( hex(cc)[2:] for cc in vv.encode( 'utf-8' ) ) )
    
    return binascii.a2b_hex( ''.join(bits) ).decode( 'utf-8' )
