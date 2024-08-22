
import re

import modules.constants as constants
from modules.token import Token

class MacroContext:
    def __init__(
        self                      ,
        inMacroDefinition = False ,
        _macros  = None           ,
        _macrovars = None           ,
    ):
        self._inMacroDefinition = inMacroDefinition
        self._macros            = _macros  or {}
        self._macrovars         = _macrovars or {}
        return
    
    def __repr__(
        self ,
    ):
        return '<MacroContext #macros=%s macrovars=%s>' % (
            len( self._macros )     ,
            repr( self._macrovars ) ,
        )
    
    def copy( self ):
        return MacroContext(
            inMacroDefinition = self._inMacroDefinition ,
            _macros           = self._macros.copy()     ,
            _macrovars        = self._macrovars.copy()  ,
        )
    
    def in_macro_definition( self ):
        return self._inMacroDefinition
    
    def set_in_macro_definition( self ):
        self._inMacroDefinition = True
    
    def has_macro( self, name ):
        return name in self._macros
    
    def add_macro( self, name, macro ):
        if name in self._macros:
            raise Exception( 'duplicate macro: %s' % repr( name ) )
        else:
            self._macros[ name ] = macro
    
    def get_macro( self, name ):
        if name not in self._macros:
            raise Exception( 'unknown macro: %s' % repr( name ) )
        else:
            return self._macros[ name ]
    
    def has_macrovar( self, name ):
        return name in self._macrovars
    
    def add_macrovar( self, name, value ):
        if name in self._macrovars:
            raise Exception( 'duplicate macro variable: %s' % repr( name ) )
        else:
            self._macrovars[ name ] = value
    
    def get_macrovar( self, name ):
        if name not in self._macrovars:
            raise Exception( 'unknown macro variable: %s' % repr( name ) )
        else:
            return self._macrovars[ name ]
    
    def expand_macrovar( self, name ):
        if re.match( '^[@][A-Za-z][A-Za-z0-9]*$', name.value() ):
            return self._as_is( name )
        else:
            return self._interpolate_word( name )
    
    def _as_is( self, name ):
        if self.has_macrovar( name.value() ):
            return self.get_macrovar( name.value() )
        else:
            raise Exception( 'unknown macrovar: %s' % repr( name ) )
        
    def _interpolate_word( self, name ):
        
        def replace_with_stringized( mm ):
            ss = mm.group('name')
            if not self.has_macrovar( ss ):
                raise Exception( 'unknown macrovar in interpolation of %s: %s' % ( repr( name ), repr( ss ) ) )
            vv = self.get_macrovar( ss )
            if vv.kind() == 'word':
                return vv.value()
            elif vv.kind() == 'integer':
                return str( vv.value() )
            elif isinstance( vv, MacroList ):
                raise Exception(
                    (
                        'you cannot expand a macrovar containing a macrolist that is touching anything else.' 
                        ' expansion rules are applied in parameters only.'
                        ' they interpolate in expansions.'
                        ' erroneous expansion: %s'
                    ) % repr( name )
                )
            else:
                raise Exception( 'some type I did not check for interpolation compatibility: %s' % repr( vv ) )
        
        interpolated = re.sub( '(?P<name>[@][A-Za-z][A-Za-z0-9]*)', replace_with_stringized, name.value() )
        
        if not interpolated:
            raise Exception( 'is this even possible?' )
        elif interpolated[0].lower() not in constants.WORDSTART:
            raise Exception( 'interpolation of %s created illegal word %s starting with non-wordstart: %s' % (
                repr( name )            ,
                repr( interpolated )    ,
                repr( interpolated[0] ) ,
            ))
        else:
            for ii in interpolated[1:]:
                if ii.lower() not in constants.WORDBITS:
                    raise Exception(
                        'interpolation of %s create illegal word %s containing non-wordbit: %s' % (
                            repr( name )         ,
                            repr( interpolated ) ,
                            repr( ii )           ,
                        )
                    )
        
        return Token(
            location = name.location() ,
            kind     = 'word'          ,
            value    = interpolated    ,
        )
