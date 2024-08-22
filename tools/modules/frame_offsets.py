
class FrameOffsets:
    
    def __init__(
        self                ,
        name                ,
        location            ,
        localvars           ,
        commands            ,
        functions           ,
        trampolineSize      ,
        trampolineEndOffset ,
    ):
        self._location = location
        
        if trampolineSize % 8 != 0:
            raise Exception( 'trampoline-size should be align 8' )
        
        if trampolineEndOffset % 8 != 0:
            raise Exception( 'trampoline-end-offset should be align 8' )
        
        trampolineSizeSlots = trampolineSize // 8
        trampolineEndOffsetSlots = trampolineEndOffset // 8
        
        self._localvars      = localvars
        self._localvarNames  = []
        self._localvarSizes  = {}
        self._localvarSlotNo = {}
        
        self._nonlocalvarNames                     = []
        self._nonlocalvarTrampolineSlotNo          = {}
        self._nonlocalvarTargetSlotNo              = {}
        self._nonlocalvarNumSlotsUsedAfterNonLocal = None
        
        # slotno is hereby defined as negative slot index to start of data from r15 cursor (which sites 1 slot past data)
        # therefore, all slots must begin at 1 and go up
        # to get the slotno, add the size in slots of the item to the current slotno
        
        slotno = 0
        
        for (localname,size) in localvars:
            if size % 8 != 0:
                raise Exception( 'implementation error: localfn size not divisible by 8: %s' % repr( (name,size) ) )
            else:
                slotno += size // 8
                
                self._localvarNames.append(localname)
                self._localvarSizes[ localname ] = size
                self._localvarSlotNo[ localname ] = slotno
                
        for cc in commands:
            if cc.kind() == 'subfn':
                if functions[ cc.value() ].is_closure( functions ):
                    
                    # slotnos are negative into the frame from r15
                    # data still points forwards, however.
                    # so for something to found immediately after something else's data
                    # it needs to be pushed immediately before that something
                    
                    slotno += 1
                    
                    self._nonlocalvarTargetSlotNo[cc.value()] = slotno
                    
                    slotno += trampolineSizeSlots
                    
                    self._nonlocalvarNames.append( cc.value() )
                    self._nonlocalvarTrampolineSlotNo[ cc.value() ] = slotno
                    
        self._slotsUsed = slotno
        
        return
    
    def frame_slots_used( self ):
        return self._slotsUsed
    
    def frame_total_size( self ):
        return self._slotsUsed * 8
    
    def is_localvar( self, name ):
        return name in self._localvars
    
    def localvars( self ):
        return self._localvars
    
    def localvars_names( self ):
        return self._localvarNames
    
    def localvar_size( self, name ):
        if name not in self._localvarSizes:
            raise Exception( 'implementation error: used name not in localvars: %s' % repr( name ) )
        else:
            return self._localvarSizes[ name ]
    
    def localvar_slotno(
        self ,
        name ,
    ):
        return self._localvarSlotNo.get( name, None )
    
    def nonlocalvar_names( self ):
        return self._nonlocalvarNames
    
    def nonlocalvar_trampoline_slotno( self, name ):
        return self._nonlocalvarTrampolineSlotNo.get( name, None )
    
    def nonlocalvar_target_slotno( self, name ):
        return self._nonlocalvarTargetSlotNo.get( name, None )
    
    def nonlocalvar_slots_used_after( self, name ):
        return self._nonlocalvarNumSlotsUsedAfterNonLocal.get( name, None )
