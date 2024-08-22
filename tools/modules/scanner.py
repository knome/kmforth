
from modules.location  import Location
from modules.character import Character
from modules.token     import Token

import modules.constants as constants

class Scanner:
    
    def parse_characters( self, data, fileSource ):
        assert isinstance( data, str )
        
        line   = 1
        column = 0
        
        for cc in data:
            yield Character(
                location = Location(
                    fileno   = fileSource.fileno() ,
                    filename = fileSource.path()   ,
                    line     = line                ,
                    column   = column              ,
                ),
                character = cc ,
            )
            
            if cc == "\n":
                line += 1
                column = 0
            else:
                column += 1

    def parse_tokens( self ,characters ):
        
        while True:
            nc = characters.take()
            if not nc:
                break
            cc = nc.character()
            
            if cc == '#':
                self.discard_comment( characters = characters )
            
            elif cc in ' \n\t':
                self.discard_whitespace( characters = characters )
            
            elif cc == '"':
                yield self.extract_string( initial = nc, characters = characters )
                
            elif cc == "`":
                yield self.extract_code( initial = nc, characters = characters )
            
            elif cc == '-' or cc in constants.NUMBERS:
                yield self.extract_number( initial = nc, characters = characters )
            
            elif cc.lower() in constants.WORDSTART or cc == '$' or cc == '&':
                yield self.extract_word( initial = nc, characters = characters )
                
            elif cc.lower() in constants.STRUCTBITS:
                yield Token(
                    location = nc.location() ,
                    kind     = cc.lower()    ,
                    value    = None          ,
                )
            
            else:
                raise Exception( 'unknown character: %s' % repr( cc ) )
    
    def discard_comment( self, characters ):
        while True:
            pc = characters.take()
            if not pc:
                break
            elif pc.character() == '\n':
                break
        return
    
    def discard_whitespace( self, characters ):
        while True:
            pc = characters.peek()
            if not pc:
                break
            elif pc.character() in ' \t\n':
                characters.take()
            else:
                break
        return
    
    def extract_string( self, initial, characters ):
        bits   = []
        escape = False
        while True:
            nc = characters.take()
            if not nc:
                raise Exception( 'unterminated string starting at: %s' % repr( initial ) )
            cc = nc.character()
            
            if escape:
                escape = False
                if cc == 'n':
                    bits.append( '\n' )
                    continue
                elif cc == '"':
                    bits.append( '"' )
                    continue
                elif cc == 't':
                    bits.append( '\t' )
                    continue
                elif cc == '0':
                    bits.append( '\0' )
                    continue
                else:
                    raise Exception( 'unknown escape: %s' % repr( '\\' + cc ) )
            else:
                if cc == '"':
                    break
                elif cc == "\\":
                    escape = True
                    continue
                else:
                    bits.append( cc )
                    continue
        
        value = ''.join( bits )
        
        kind = 'string'
        if '@' in value:
            kind = 'macrostring'
        
        return Token(
            location = initial.location() ,
            kind     = kind               ,
            value    = value              ,
        )
    
    def extract_number( self, initial, characters ):
        
        if initial.character() == '-' and ( ( not characters.peek() ) or ( characters.peek().character() not in constants.NUMBERS ) ):
            return self.extract_word( initial, characters )
        
        bits = [ initial.character() ]
        while True:
            pc = characters.peek()
            if not pc:
                break
            cc = pc.character()
            if cc.lower() in '0123456789.xoabcdef':
                bits.append( cc )
                characters.take()
                continue
            else:
                break
        
        value = ''.join( bits )
        given = value
        
        try:
            negative = False
            if value.startswith('-'):
                value    = value[1:]
                negative = True
            
            if '-' in value:
                raise Exception( '"-" in number other than at start: %s' % repr( given ) )
            
            if '.' in value:
                raise Exception( 'float not currently handled' )
            
            base = 10
            if value.startswith( '0x' ):
                base = 16
                value = value[2:]
            elif value.startswith( '0o' ):
                base = 8
                value = value[2:]
            elif value.startswith( '0b' ):
                base = 2
                value = value[2:]
            
            # should throw if any trash is left in the number
            value = int( value, base )
            
            if negative:
                value = -value
            
        except ValueError as err:
            raise Exception( 'error parsing number: %s' % repr( given ) )
        
        tt = Token(
            location = initial.location() ,
            kind     = 'integer'          ,
            value    = value              ,
        )
        
        return tt
    
    def extract_code( self, initial, characters ):
        bits = []
        while True:
            pc = characters.take()
            if not pc:
                raise Exception( 'unterminated code segment starting at: %s' % repr( initial ) )
            cc = pc.character()
            if cc == '`':
                break
            else:
                bits.append( cc )
            
        value = ''.join(bits)
        if '@' in bits:
            kind = 'macrocode'
        else:
            kind = 'code'
        
        return Token(
            location = initial.location() ,
            kind     = kind               ,
            value    = value              ,
        )
    
    def extract_word( self, initial, characters ):
        bits = [ initial.character() ]
        while True:
            pc = characters.peek()
            if not pc:
                break
            cc = pc.character()
            if cc.lower() in constants.WORDBITS or cc == '$':
                characters.take()
                bits.append( cc )
            else:
                break
        
        if initial.character() == '$':
            kind  = 'localfn'
            value = ''.join(bits)
        elif initial.character() == '&':
            kind  = 'fnref'
            value = ''.join(bits)[1:]
        elif initial.character() == '@' or '@' in bits:
            if len( bits ) == 1:
                kind  = '@'
                value = None
            else:
                kind  = 'macrovar'
                value = ''.join(bits)
        else:
            kind  = 'word'
            value = ''.join(bits)
        
        token = Token(
            location = initial.location() ,
            kind     = kind               ,
            value    = value              ,
        )
        
        if value and '$' in value[1:]:
            raise Exception(
                '"$" cannot be used inside a word, just at the start of a local, found: %s' % repr( token )
            )
        
        return token
    
    def extract_macrovar( self, initial, characters ):
        bits = []
        while True:
            pc = characters.peek()
            if not pc:
                break
            elif pc.character().lower() not in WORDBITS:
                break
            
            characters.take()
            bits.append( pc.character() )
        
        value = ''.join( bits )
        
        if value == '':
            return Token(
                location = initial.location() ,
                kind     = '@'                ,
                value    = None               ,
            )
        else:
            return Token(
                location = initial.location() ,
                kind     = 'macrovar'         ,
                value    = value              ,
            )
