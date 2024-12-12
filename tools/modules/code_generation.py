
from modules.string_coalescer import StringCoalescer
from modules.uniques          import Uniques
from modules.mangling         import mangle, unmangle
from modules.source           import Source

def generate_code(
    options             ,
    functions           ,
    usedFunctions       ,
    startname           ,
    trampolineSize      ,
    trampolineEndOffset ,
):
    stringCoalescer = StringCoalescer()
    
    staticStrings = set()
    
    pre  = []
    data = []
    code = []
    bss  = []
    
    uniques = Uniques()
    
    bss.append( 'section .bss\n' )
    bss.append( 'datastack: resq 1\n' )
    bss.append( 'callstack: resq 1\n' )
    bss.append( '\n' )
    
    data.append( 'section .data\n' )
    data.append( '\n' )
    
    code.append( 'section .text\n' )
    
    code.append( 'global _start\n')
    code.append( '\n')
    
    code.append( '; this trampoline is copied into the stack to enable closures\n' )
    code.append( '; it uses position independent instruction-pointer relative load effective address\n' )
    code.append( '; to find its jump return. it also ensures the return jump takes up the space we think it does\n' )
    code.append( '; we copy this into a stack frame for each closure the function references\n' )
    code.append( '; then, instead of passing the value of the closure, we pass this thing\n')
    code.append( '; when someone goes to call the closure, it calls this, which is in the stack of the binding callframe\n')
    code.append( '; this pushes its return address and jumps to the actual function to be called\n' )
    code.append( '; that function then resolves any parent locals relative to the return address, as they will follow the closures\n')
    code.append( '; this allows us to send a normal x64 points around, but one that is able to find its origin frame and locals!\n')
    code.append( '; this will make debugging hell and make any stack corruption a hundred times worse\n')
    code.append( '; it is perfect for kmforth\n')
    code.append( ' align 64\n')
    code.append( '_trampoline:\n')
    code.append( ' lea rax, [rel .trampoline_return]\n')
    code.append( ' mov [r15], rax\n')
    code.append( ' add r15, 8\n')
    code.append( ' mov rax, qword [rel .trampoline_target]\n')
    code.append( ' jmp rax\n' )
    code.append( ' align 8\n' )
    code.append( '.trampoline_return:\n')
    code.append( ' sub r15, 8\n' )
    code.append( ' jmp [r15]\n' )
    code.append( ' align 8\n' )
    code.append( '.trampoline_target:\n')
    code.append( '\n')
    code.append( '\n' )
    code.append( 'align 64\n')
    code.append( '_start:\n' )
    code.append( '    jmp %s\n' % startname )
    code.append( '\n')
    
    nn = 0
    for fn in functions:
        
        # 'tree shaking'
        if fn not in usedFunctions:
            continue
        
        code.append( '\n' )
        code.append( '; %s\n' % repr( functions[fn].location() ) )
        code.append( '  ' + fn + ':\n' )
        
        localfns = LocalFns(
            uniques             = uniques             ,
            functions           = functions           ,
            fn                  = fn                  ,
            trampolineSize      = trampolineSize      ,
            trampolineEndOffset = trampolineEndOffset ,
        )
        
        frameOffsets = functions[ fn ].body_details().frame_offsets(
            functions           = functions           ,
            trampolineSize      = trampolineSize      ,
            trampolineEndOffset = trampolineEndOffset ,
        )
        
        if frameOffsets.frame_total_size():
            code.append( '  ; make space for any closure trampolines and locals\n' )
            code.append( '  add r15, %d\n' % ( frameOffsets.frame_total_size() ) )

        if trampolineSize != 32:
            raise Exception( 'need to make this general' )
        
        for closureName in frameOffsets.nonlocalvar_names():
            code.append( ' ; copy the trampoline code into the stack\n' )
            code.append( '  mov rax, [_trampoline]\n' )
            code.append( '  mov qword [r15-8*%d], rax\n' % (
                frameOffsets.nonlocalvar_trampoline_slotno( closureName ),
            ))
            code.append( '  mov rax, [_trampoline+8]\n' )
            code.append( '  mov qword [r15-8*%d+8], rax\n' % (
                frameOffsets.nonlocalvar_trampoline_slotno( closureName ),
            ))
            code.append( '  mov rax, [_trampoline+16]\n' )
            code.append( '  mov qword [r15-8*%d+16], rax\n' % (
                frameOffsets.nonlocalvar_trampoline_slotno( closureName ),
            ))
            code.append( '  mov rax, [_trampoline+24]\n' )
            code.append( '  mov qword [r15-8*%d+24], rax\n' % (
                frameOffsets.nonlocalvar_trampoline_slotno( closureName ),
            ))
            code.append( ' ; and the trampoline target right after it\n' )
            code.append( '  mov qword [r15-8*%d], %s\n' % (
                frameOffsets.nonlocalvar_target_slotno( closureName ),
                closureName
            ))
        
        for command in functions[ fn ].body_details().commands():
            
            if command.kind() == 'word':
                rt = '.' + fn + '_' + str( nn )
                nn = nn + 1
                
                code.append( '    ; calling %s\n' % unmangle(command.value()) )
                code.append( '    mov qword [r15], %s\n' % rt )
                code.append( '    add r15, 8\n' )
                code.append( '    jmp ' + command.value() + '\n' )
                code.append( '  %s:\n' % rt )
                
            elif command.kind() == 'code':
                code.append( '\n' )
                code.append( '; including code literal\n' )
                code.append( fetch_code(
                    options = options         ,
                    data    = command.value() ,
                ))
                code.append( '\n' )
                
            elif command.kind() == 'string':
                
                sn = stringCoalescer.lookup( command.value() )
                if not sn:
                    sn = "km_c_" + str(uniques.get())
                    data.append( '  ' + sn + ':\n' )
                    # convert \n into 10 here ( 10, 13 for windows, but fuck those guys
                    data.append( "    db %s\n" % asm_stringize( command.value() ) )
                    stringCoalescer.remember( command.value(), sn )
                    
                code.append( '   ; pushing string literal %s\n' % repr( command.value() ) )
                code.append( '   mov qword [r14], %s\n' % sn )
                code.append( '   add r14, 8\n' )
                
            elif command.kind() == 'integer':
                # 
                # you can't write an immediate larger than a 32bit value directly to memory
                # you have to load the value into a register and use the register command form
                # 
                if command.value() > (4294967296 - 1):
                    code.append( '   ; push integer > 32bit\n' )
                    code.append( '   mov rax, %s\n' % command.value() )
                    code.append( '   mov [r14],rax\n' )
                    code.append( '   add r14,8\n' )
                else:
                    code.append( '   ; push integer < 32bit\n' )
                    code.append( '   mov qword [r14], %s\n' % command.value() )
                    code.append( '   add r14, 8\n' )
            
            # user code can't create a FORWARDJUMPIF, but optimization passes can
            elif command.kind() == 'FORWARDJUMPIF':
                code.append( INLINED_LEAVEIF % { 'endlabel' : command.value() } )
                
            # user code can't create a JUMPTARGET, but optimization passes can
            elif command.kind() == 'JUMPTARGET':
                code.append( command.value() + ":\n" )
            
            elif command.kind() == 'localfn':
                if command.value().startswith('$.'):
                    builtin = command.value()
                    # no localfn for unconditional call, just use 'call'
                    if builtin == '$.callIf':
                        localfns.implementation_callIf( code )
                    elif builtin == '$.jumpIf':
                        localfns.implementation_jumpIf( code )
                    elif builtin == '$.jump':
                        localfns.implementation_jump( code )
                    elif builtin == '$.leaveIf':
                        localfns.implementation_leaveIf( code )
                    elif builtin == '$.call':
                        localfns.implementation_call( code )
                    elif builtin == '$.noopt':
                        # this just prevents inlining the function or inlining into the function
                        pass
                    else:
                        raise Exception( 'unknown builtin localfn: %s' % repr( command.value() ) )
                else:
                    # locals getters and setters
                    commandBits = command.value().split('.',1)
                    if len( commandBits ) != 2:
                        raise Exception( 'command-bits length not 2? %s' % repr( commandBits ) )
                    localName, memberfn = commandBits
                    
                    localvar = localfns.localvar( localName )
                    
                    if memberfn == 'get':
                        localvar.implementation_get( code )
                    elif memberfn == 'set':
                        localvar.implementation_set( code )
                    elif memberfn == 'update':
                        localvar.implementation_update( code )
                    elif memberfn == 'call':
                        localvar.implementation_call( code )
                    elif memberfn == 'copy':
                        localvar.implementation_copy( code )
                    elif memberfn == 'here':
                        localvar.implementation_here( code )
                    elif memberfn == 'jump':
                        localvar.implementation_jump( code )
                    elif memberfn == 'jumpIf':
                        localvar.implementation_jumpIf( code )
                    elif memberfn == 'addr':
                        localvar.implementation_addr( code )
                    elif memberfn == 'incr':
                        localvar.implementation_incr( code )
                    elif memberfn == 'decr':
                        localvar.implementation_decr( code )
                    else:
                        raise Exception( 'unknown localfn ( expecting <local>.get or <local>.set ): %s' % repr( command.value() ) )
                    
            elif command.kind() == 'fnref':
                code.append( '    ; push reference to fn\n' )
                code.append( '    mov qword [r14], %s\n' % command.value() )
                code.append( '    add r14, 8\n' )
                
            elif command.kind() == 'subfn':
                if functions[ command.value() ].is_closure( functions ):
                    # needs a trampoline for nonlocal access
                    code.append( ' ; for subfn, push closure (%s) trampoline reference\n' % repr( command.value() ))
                    code.append( ' lea rax, [r15+8*%d]\n' % (- frameOffsets.nonlocalvar_trampoline_slotno( command.value())))
                    code.append( ' mov qword [r14], rax\n' )
                    code.append( ' add r14, 8\n' )
                else:
                    # normal c-style function pointer
                    code.append( '    ; push subfn reference\n' )
                    code.append( '    mov qword [r14], %s\n' % command.value() )
                    code.append( '    add r14, 8\n' )
            else:
                raise Exception( 'wat %s %s' % ( str( command.kind() ), repr( command.value() ) ) )
        
        if frameOffsets.frame_total_size():
            code.append( '    ; pop any trampolines and locals\n' )
            code.append( '    sub r15, %d\n' % ( frameOffsets.frame_total_size() ) )
            
        code.append( '    ; pop and jump to caller\n' )
        code.append( '    sub r15, 8\n' )
        code.append( '    jmp [r15]\n' )
        
    return '\n'.join( [''.join(pre), ''.join( data ), ''.join( code ), ''.join( bss ) ] )
    
    
class LocalFns:
    def __init__(
        self                ,
        uniques             ,
        functions           ,
        fn                  ,
        trampolineSize      ,
        trampolineEndOffset ,
    ):
        self._uniques             = uniques
        self._functions           = functions
        self._fn                  = fn
        self._trampolineSize      = trampolineSize
        self._trampolineEndOffset = trampolineEndOffset
        
        self._frameOffsets = functions[ fn ].body_details().frame_offsets(
            functions           = functions           ,
            trampolineSize      = trampolineSize      ,
            trampolineEndOffset = trampolineEndOffset ,
        )
        
        self._body = functions[ fn ].body_details()
        return
    
    def localvar( self, localVarName ):
        return LocalVarFns(
            uniques             = self._uniques             ,
            functions           = self._functions           ,
            fn                  = self._fn                  ,
            localVarName        = localVarName              ,
            frameOffsets        = self._frameOffsets        ,
            trampolineSize      = self._trampolineSize      ,
            trampolineEndOffset = self._trampolineEndOffset ,
        )
    
    def implementation_callIf( self, code ):
        label = '.km_nocall_' + str(self._uniques.get())
        code.append( '    ; callIf localfn\n' )
        code.append( '    sub r14, 8\n' )                  # pop todo
        code.append( '    mov rax, [r14]\n' )
        code.append( '    sub r14, 8\n' )                  # pop cond
        code.append( '    mov rbx, [r14]\n' )
        code.append( '    test rbx,rbx\n' )                # test setting zf
        code.append( '    jz %s\n' % label )               # jump over call if 0
        code.append( '    mov qword [r15], %s\n' % label ) # push return label onto callstack
        code.append( '    add r15, 8\n' )
        code.append( '    jmp rax\n' )                     # go
        code.append( '   %s:\n' % label )                  # return label
        
    def implementation_jumpIf( self, code ):
        label = '.km_nojump_' + str(self._uniques.get())
        code.append( '    ; jumpIf \n' )
        code.append( '    sub r14, 8\n' )     # pop jump target
        code.append( '    mov rax, [r14]\n' )
        code.append( '    sub r14, 8\n' )     # pop cond
        code.append( '    mov rbx, [r14]\n' )
        code.append( '    test rbx,rbx\n' )   # test cond
        code.append( '    jz %s\n' % label )  # jump over jump if 0
        code.append( '    jmp rax\n' )        # jump
        code.append( '   %s:\n' % label )     # don't
        
    def implementation_jump( self, code ):
        code.append( '    ; jump\n' )
        code.append( '    sub r14, 8\n' )
        code.append( '    jmp [r14]\n' )
        
    def implementation_leaveIf( self, code ):
        label = '.km_noleave_' + str(self._uniques.get())
        code.append( '    ; leaveIf\n' )
        code.append( '    sub r14, 8\n' )
        code.append( '    mov rax, [r14]\n' )
        code.append( '    test rax,rax\n' )
        code.append( '    jz %s\n' % label )
        if self._frameOffsets.frame_total_size():
            code.append( '    ; (popping locals before leaving)\n' )
            code.append( '    sub r15, %d\n' % ( self._frameOffsets.frame_total_size() ) )
        code.append( '    sub r15, 8\n' )
        code.append( '    jmp [r15]\n' )
        code.append( '   %s:\n' % label )
        
    def implementation_call( self, code ):
        label = '.km_return_'+  str(self._uniques.get())
        code.append( '    ; $.call\n' )
        code.append( '    mov qword [r15], %s\n' % label )
        code.append( '    add r15, 8\n' )
        code.append( '    sub r14, 8\n' )
        code.append( '    jmp [r14]\n' )
        code.append( label + ':\n' )
        

# we don't need to care what the parent is in the code, just how many indirections
# are required to get to a certain variable. we will then need to make usage of that
# variable perform the correct number of parent hops and get/set/addr the local in
# the resulting frame.
# we always know the number of hops for a given variable, because a closer is only
# created by having them inside other functions or closures
# 
class LocalVarFns:
    def __init__(
        self                ,
        uniques             ,
        functions           ,
        fn                  ,
        localVarName        ,
        frameOffsets        ,
        trampolineSize      ,
        trampolineEndOffset ,
    ):
        self._uniques             = uniques
        self._functions           = functions
        self._fn                  = fn
        self._localVarName        = localVarName
        self._frameOffsets        = frameOffsets
        self._trampolineSize      = trampolineSize
        self._trampolineEndOffset = trampolineEndOffset
        
        self._slotno, self._indirections = self._determine_slotno_and_indirections(
            trampolineSize      = trampolineSize      ,
            trampolineEndOffset = trampolineEndOffset ,
        )
        
        return
    
    def _determine_slotno_and_indirections(
        self                ,
        trampolineSize      ,
        trampolineEndOffset ,
    ):
        indirections = []
        cfn = self._fn
        while True:
            frameOffsets = self._functions[ cfn ].body_details().frame_offsets(
                functions           = self._functions     ,
                trampolineSize      = trampolineSize      ,
                trampolineEndOffset = trampolineEndOffset ,
            )
            slotno = frameOffsets.localvar_slotno( self._localVarName )
            if slotno != None:
                break
            
            cfn = self._functions[ cfn ].parent()
            indirections.append( cfn )
            
            if cfn != None:
                continue
            else:
                raise Exception( 'cannot locate localvar named (%s) in function (%s @ %s)' % (
                    repr(self._localVarName),
                    repr(self._fn),
                    repr(self._functions[self._fn].location()),
                ))
        return slotno, indirections
    
    def _walk_to_target_frame( self, code ):
        code.append( ' ; walking trampoline\n' )
        code.append( ' ; get return-address\n' )
        # the return address is one slot past the end of the frame
        code.append( ' mov rax, [r15+8*%d+8*%d]\n' % (
            - self._frameOffsets.frame_slots_used(),
            - 1
        ))
        remaining = list( self._indirections )
        last = remaining.pop()
        penultimate = self._fn
        for cfn in remaining:
            parentFrameOffsets = self._functions[ cfn ].body_details().frame_offsets(
                functions           = self._functions           ,
                trampolineSize      = self._trampolineSize      ,
                trampolineEndOffset = self._trampolineEndOffset ,
            )
            code.append( ' ; get next return-address\n' )
            code.append( ' mov rax, [rax+8*%d+8*%d+8*%d+8*%d+8*%d]\n' % (
                + (self._trampolineEndOffset // 8),
                - (self._trampolineSize // 8),
                + parentFrameOffsets.nonlocalvar_trampoline_slotno( penultimate ),
                - parentFrameOffsets.frame_slots_used(),
                - 1,
            ))
            penultimate = cfn
        lastFrameOffsets = self._functions[ last ].body_details().frame_offsets(
            functions           = self._functions           ,
            trampolineSize      = self._trampolineSize      ,
            trampolineEndOffset = self._trampolineEndOffset ,
        )
        return last, lastFrameOffsets, '[rax+8*%d+8*%d+8*%d+8*%d]' % (
                + (self._trampolineEndOffset // 8),
                - (self._trampolineSize // 8),
                + lastFrameOffsets.nonlocalvar_trampoline_slotno( penultimate ),
                - lastFrameOffsets.localvar_slotno( self._localVarName ),
        )

    def _require_slot_sized( self, getSizeFn, name ):
        if getSizeFn( name ) != 8:
            a = 'you can only .get, .set, .update, .call and .here vars of size 8. other sizes only offer .addr, '
            b = 'found %s in %s which is size %s' % (
                repr( name ),
                repr( unmangle( self._fn ) ),
                repr( getSizeFn( name ) ) ,
            )
            raise Exception( a + b )
    
    def implementation_get( self, code ):
        if self._indirections:
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( parentOffsets.localvar_size, self._localVarName )
            code.append( '   ; push nonlocal (%s) to datastack\n' % repr( self._localVarName ) )
            code.append( '   mov rax, %s\n' % addr )
            code.append( '   mov qword [r14], rax\n' )
            code.append( '   add r14, 8\n' )
            return
        else:
            self._require_slot_sized( self._frameOffsets.localvar_size, self._localVarName )
            code.append( '    ; push local (%s) to datastack\n' % repr( self._localVarName ) )
            code.append( '    mov rax, [r15-8*%d]\n' % (self._slotno) )
            code.append( '    mov qword [r14], rax\n' )
            code.append( '    add r14, 8\n' )
        
    def implementation_set( self, code ):
        if self._indirections:
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( parentOffsets.localvar_size, self._localVarName )
            code.append( '    ; pop datastack storing to nonlocal (%s)\n' % repr( self._localVarName ))
            code.append( '    sub r14, 8\n')
            code.append( '    mov rbx, [r14]\n' )
            code.append( '    mov qword %s, rbx\n' % addr )
        else:
            self._require_slot_sized( self._frameOffsets.localvar_size, self._localVarName )
            code.append( '    ; pop datastack storing to local (%s)\n' % ( repr( self._localVarName ) ) )
            code.append( '    sub r14, 8\n' )
            code.append( '    mov rax, [r14]\n' )
            code.append( '    mov qword [r15-8*%d], rax\n' % (self._slotno) )
            
    def implementation_update( self, code ):
        if self._indirections:
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( parentOffsets.localvar_size, self._localVarName )
            label = '.km_update_nonlocal_' + str(self._uniques.get())
            code.append('    ; update value of nonlocal %s by getting, invoking and setting\n' % repr( self._localVarName ))
            code.append('    mov rbx, [r14-8]\n')
            code.append('    mov rax, %s\n' % addr)
            code.append('    mov [r14-8], rax\n')
            code.append('    mov qword [r15], %s\n' % label)
            code.append('    add r15, 8\n')
            code.append('    jmp rbx\n')
            code.append(' %s:\n' % label)
            # recalculate addr because we don't have anywhere to save it and registers aren't save across calls
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            code.append('    mov rbx, [r14-8]\n')
            code.append('    sub r14, 8\n')
            code.append('    mov qword %s, rbx\n' % addr)
            code.append('    ; end non-local update\n')
        else:
            self._require_slot_sized( self._frameOffsets.localvar_size, self._localVarName )
            label = '.km_update_local_' + str(self._uniques.get())
            code.append('    ; update value of local %s by getting, invoking and setting\n' % repr( self._localVarName ))
            code.append('    mov rbx, [r14-8]\n')
            code.append('    mov rax, [r15+8*%d]\n' % (- self._slotno))
            code.append('    mov qword [r14-8], rax\n')
            code.append('    mov qword [r15], %s\n' % label)
            code.append('    add r15, 8\n')
            code.append('    jmp rbx\n')
            code.append(' %s:\n' % label)
            code.append('    mov rax, [r14-8]\n')
            code.append('    sub r14, 8\n')
            code.append('    mov qword [r15+8*%d], rax\n' % (- self._slotno))
            code.append('    ; end local update\n')
    
    def implementation_call( self, code ):
        if self._indirections:
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( parentOffsets.localvar_size, self._localVarName )
            label = '.km_call_nonlocal_' + str(self._uniques.get())
            code.append( '    mov qword [r15], %s\n' % label )
            code.append( '    add r15, 8\n' )
            code.append( '    jmp %s\n' % addr )
            code.append( ' %s:\n' % label )
        else:
            label = '.km_call_local_' + str(self._uniques.get())
            code.append( '    mov rbx, [r15+8*%d]\n' % (- self._slotno))
            code.append( '    mov qword [r15], %s\n' % label )
            code.append( '    add r15, 8\n' )
            code.append( '    jmp rbx\n' )
            code.append( ' %s:\n' % label )
    
    def implementation_copy( self, code ):
        if self._indirections:
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( parentOffsets.localvar_size, self._localVarName )
            code.append( '    ; copy top of datastack to nonlocal (%s)\n' % ( repr( self._localVarName ) ) )
            code.append( '    mov rbx, [r14-8]\n' )
            code.append( '    mov qword %s, rbx\n' % addr )
        else:
            self._require_slot_sized( self._frameOffsets.localvar_size, self._localVarName )
            code.append( '    ; copy datastack to local (%s)\n' % ( repr( self._localVarName ) ) )
            code.append( '    mov rax, [r14-8]\n' )
            code.append( '    mov qword [r15-8*%d], rax\n' % (self._slotno) )
    
    def implementation_here( self, code ):
        if self._indirections:
            # 
            # there is no reasonable reason to ever store a nonlocal here
            # I'll allow it
            #
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( self._parentOffsets.localvar_size, self._localVarName )
            label = '.km_here_nonlocal_' + str(self._uniques.get())
            code.append( '    ; set local (%s) to label following this command\n' % repr(self._localVarName) )
            code.append( '    mov qword %s, %s\n' % (addr, label))
            code.append( '    %s:\n' % label )
        else:
            self._require_slot_sized( self._frameOffsets.localvar_size, self._localVarName )
            label = '.km_here_' + str(self._uniques.get())
            code.append( '    ; set local (%s) to label following this command\n' % repr(self._localVarName))
            code.append( '    mov qword [r15-8*%d], %s\n' % ( (self._slotno), label) )
            code.append( '    %s:\n' % label )
        
    def implementation_jump( self, code ):
        if self._indirections:
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( parentOffsets.localvar_size, self._localVarName )
            code.append( '    jump %s\n' % addr )
        else:
            self._require_slot_sized( self._frameOffsets.localvar_size, self._localVarName )
            code.append( '    jmp qword [r15+8*%d]\n' % (- self._slotno) )
        
    def implementation_jumpIf( self, code ):
        if self._indirections:
            label = '.km_dont_jumpif_nonlocal_' + str(self._uniques.get())
            code.append( '    sub r14,8\n' )
            code.append( '    mov rbx,[r14]\n' )
            code.append( '    test rbx,rbx\n' )
            code.append( '    jz %s\n' % label )
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( parentOffsets.loclvar_size, self._localVarName )
            code.append( '    jmp %s\n' % addr )
            code.append( '%s:\n' % label )
        else:
            self._require_slot_sized( self._frameOffsets.localvar_size, self._localVarName )
            label = '.km_dont_jumpif_' + str(self._uniques.get())
            code.append( '    sub r14,8\n' )
            code.append( '    mov rax,[r14]\n' )
            code.append( '    test rax,rax\n' )
            code.append( '    jz %s\n' % label )
            code.append( '    jmp [r15-8*%d]\n' % (self._slotno) )
            code.append( '%s:\n' % label )

    def implementation_addr( self, code ):
        if self._indirections:
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            code.append( '    ; push address of nonlocal (%s) onto stack\n' % repr( self._localVarName ) )
            code.append( '    lea rax, %s\n' % addr )
            code.append( '    mov [r14],rax\n' )
            code.append( '    add r14,8\n' )
        else:
            code.append( '    ; push address of local (%s) onto stack\n' % repr( self._localVarName ) )
            code.append( '    lea  rax,[r15-8*%d]\n' % (self._slotno) )
            code.append( '    mov  [r14],rax\n' )
            code.append( '    add  r14,8\n' )
        
    def implementation_incr( self, code ):
        if self._indirections:
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( parentOffsets.localvar_size, self._localVarName )
            code.append( '    ; incr nonlocal (%s) in-place\n' % repr( self._localVarName ) )
            code.append( '    inc qword %s\n' % addr )
        else:
            self._require_slot_sized( self._frameOffsets.localvar_size, self._localVarName )
            code.append( '    ; incr local (%s) in-place\n' % repr( self._localVarName ) )
            code.append( '    inc qword [r15-8*%d]\n' % (self._slotno) )

    def implementation_decr( self, code ):
        if self._indirections:
            parent, parentOffsets, addr = self._walk_to_target_frame( code )
            self._require_slot_sized( parentOffsets.localvar_size, self._localVarName )
            code.append( '    ; decr nonlocal (%s) in-place\n' % repr( self._localVarName ) )
            code.append( '    dec qword %s\n' % addr )
        else:
            self._require_slot_sized( self._frameOffsets.localvar_size, self._localVarName )
            code.append( '    ; decr local (%s) in-place\n' % repr( self._localVarName ) )
            code.append( '    dec qword [r15-8*%d]\n' % (self._slotno) )
    
def asm_stringize( ss ):
    bits      = []
    instr     = False
    for cc in ss:
        if cc.lower() in ' abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()[]{}|,:-/':
            if instr:
                bits.append( cc )
                continue
            else:
                if bits:
                    bits.append( ',' )
                bits.append( "'" )
                bits.append( cc )
                instr = True
        else:
            if instr:
                bits.append( "'")
                instr = False
            first = None
            for bit in cc.encode('utf-8').hex():
                if first == None:
                    first = bit
                else:
                    if bits:
                        bits.append( ',' )
                    bits.append( '0x' + first + bit )
                    first = None
    if instr:
        bits.append( "'" )
    
    if bits:
        bits.append(',')
    
    bits.append( '0' )
    
    return ''.join( bits )

def fetch_code( options, data ):
    if '===' not in data:
        return data
    
    for section in parse_code_sections( options, data ):
        
        if not (section['headers'].get('impl', options.implementation) == options.implementation):
            if options.showOptimizations:
                debug( '[fetch-code] skipping section, wrong impl: %s' % repr( section ) )
            continue
        
        if not (section['headers'].get('type','code') == 'code'):
            if options.showOptimizations:
                debug( '[fetch-code] skipping section, wrong type: %s' % repr( section ) )
            continue
        
        if not (section['headers'].get('when', '').strip() == ''):
            if options.showOptimizations:
                debug( '[fetch-code] skipping section, has conditional: %s' % repr( section ) )
            continue
        
        return section['body']
    
    raise Exception( 'no appropriate code section found: %s' % repr( data ) )
    
def parse_code_sections( impl, data ):
    lines = Source( data.strip().split('\n') )
    
    done = False
    sections = []
    while True:
        headers = {}
        while True:
            line = lines.take()
            if line == None:
                done = True
                break
            elif '===' in line:
                raise Exception( 'cannot have === in headers section, separate headers by at least one blank line, in %s' % (
                    repr( data ) ,
                ))
            elif line.strip() == "":
                break
            else:
                name, value = line.strip().split(':',1)
                name = name.strip()
                value = value.strip()
                headers[ name ] = value
        
        if done:
            break
        
        body = []
        while True:
            line = lines.take()
            if line == None:
                done = True
                break
            elif '===' in line:
                break
            else:
                body.append( line )
        
        sections.append({'headers' : headers, 'body' : '\n'.join(body) + '\n'})
        
        if done:
            break
    
    return sections

def unparse_code_sections( sections ):
    bits = []
    
    for section in sections:
        for header in section['headers'].items():
            bits.append( '%s : %s' % ( header[0], header[1] ) )
        
        bits.append( '' )
        
        bits.append( section['body'] )
        
        bits.append( '===' )
    
    return '\n'.join( bits[:-1] )

