
from modules.frame_offsets import FrameOffsets

class Body:
    
    def rewriting_commands( self, new ):
        return Body(
            location  = self._location  ,
            commands  = new             ,
            localargs = self._localargs ,
            localvars = self._localvars ,
            subfns    = self._subfns    ,
        )
    
    def rewriting_locals( self, new ):
        return Body(
            location  = self._location  ,
            commands  = self._commands  ,
            localargs = self._localargs ,
            localvars = new             ,
            subfns    = self._subfns    ,
        )
    
    def rewriting_nonlocals( self, name, varupdates ):
        # 
        # don't rewrite matches to our args
        # do rewrite any other matching locals
        # the caller recurses so we don't have to
        # caller also responsible for cleaning out locals
        # so if they are there, don't
        
        localvars = dict(self._localvars)
        
        for varname in varupdates:
            if varname in self._localargs:
                raise Exception('implementation error: nonlocal rewrite contains local: %s' % repr(varname))
        
        newcommands = []
        for command in self._commands:
            if command.kind() == 'localfn':
                if not command.value().startswith('$.'):
                    name, action = command.value().split('.',1)
                    if name in varupdates:
                        newcommands.append(Token(
                            location = command.location() ,
                            kind     = 'localfn',
                            value    = varupdates[name] + '.' + action
                        ))
                    else:
                        newcommands.append(command)
                else:
                    newcommands.append(command)
            else:
                newcommands.append(command)
        
        return Body(
            location  = self._location  ,
            commands  = newcommands     ,
            localargs = self._localargs ,
            localvars = self._localvars ,
            subfns    = self._subfns    ,
        )
    
    def rewriting_subfns( self, updates ):
        newcommands = []
        for command in self._commands:
            if command.kind() == 'subfn':
                if command.value() in updates:
                    newcommands.append(Token(
                        location = command.location() ,
                        kind     = 'subfn' ,
                        value    = updates[command.value()] ,
                    ))
                else:
                    newcommands.append( command )
            else:
                newcommands.append( command )
        
        return Body(
            location  = self._location  ,
            commands  = newcommands     ,
            localargs = self._localargs ,
            localvars = self._localvars ,
            subfns    = self._subfns    ,
        )
    
    def __init__(
        self      ,
        location  ,
        commands  ,
        localargs ,
        localvars ,
        subfns    ,
    ):
        self._location  = location
        self._commands  = commands
        self._localargs = localargs
        self._localvars = localvars
        self._subfns    = subfns
    
    def location(self):  return self._location
    def commands(self):  return self._commands
    def localargs(self): return self._localargs
    def localvars(self): return self._localvars
    def subfns(self):    return self._subfns
    
    def body_details( self, name ):
        return BodyDetails(
            name      = name            ,
            location  = self._location  ,
            commands  = self._commands  ,
            localvars = self._localvars ,
            subfns    = self._subfns    ,
        )

class BodyDetails:
    
    def __init__(
        self      ,
        name      ,
        location  ,
        commands  ,
        localvars ,
        subfns    ,
    ):
        self._name      = name
        self._location  = location
        self._commands  = commands
        self._localvars = localvars
        self._subfns    = subfns
    
    def location( self ):
        return self._location
    
    def __repr__( self ):
        return '<Definition %s command.cnt=%s>' % (
            repr( self._location )        ,
            repr( len( self._commands ) ) ,
        )
    
    def is_closure( self, functions ):
        unresolvedNonLocals = list( self.unresolved_nonlocals( functions ) )
        return bool( len( unresolvedNonLocals ) )
    
    def has_local(self, name):
        return any(name == localname for localvar in self._localvars for (localname,localsize) in [localvar])
    
    def unresolved_nonlocals( self, functions ):
        for command in self._commands:
            if command.kind() == 'localfn':
                if not command.value().startswith('$.'):
                    if '.' not in command.value():
                        raise Exception( 'malformed localfn or localvar: %s' % repr( command ) )
                    name, _ = command.value().split('.',1)
                    if not self.has_local(name):
                        yield name
            
            if command.kind() == 'subfn':
                for unresolvedNonLocal in functions[ command.value() ].body_details().unresolved_nonlocals( functions ):
                    if not self.has_local(unresolvedNonLocal):
                        yield unresolvedNonLocal
    
    def localvars( self ):
        return self._localvars
    
    def subfns( self ):
        return self._subfns
    
    def commands( self ):
        return self._commands
    
    def frame_offsets(
        self                ,
        functions           ,
        trampolineSize      ,
        trampolineEndOffset ,
    ):
        return FrameOffsets(
            name                = self._name          ,
            location            = self._location      ,
            localvars           = self._localvars     ,
            commands            = self._commands      ,
            functions           = functions           ,
            trampolineSize      = trampolineSize      ,
            trampolineEndOffset = trampolineEndOffset ,
        )

