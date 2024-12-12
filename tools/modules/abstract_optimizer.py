
from modules.abstract_code import AbstractCode

def optimize_abstract(
    abstract ,
):
    while True:
        print('optimizing...')
        abstract, changed = perform_abstract_optimization(abstract)
        if not changed:
            return abstract

def perform_abstract_optimization(
    abstract ,
):
    newAbstract = AbstractCode( startname = abstract.startname() )
    
    anyChanged = False
    for f in abstract.functions():
        
        newFunction = newAbstract.new_function( functionName = f.name() )
        
        if not f.optimizable():
            instructions = f.instructions()
            changed      = False
        else:
            instructions, changed = perform_function_optimization(
                abstract  = abstract            ,
                instructions = f.instructions() ,
            )
        
        for instruction in instructions:
            newFunction.add_instruction(instruction)
        
        anyChanged = anyChanged or changed
    
    return newAbstract, anyChanged

def perform_function_optimization(
    abstract     ,
    instructions ,
):
    anyChanged = False
    
    for optimization in [
        optimization_inline_nonclosures_without_code ,
    ]:
        instructions, changed = optimization(abstract, instructions)
        anyChanged = anyChanged or changed
        
    return instructions, anyChanged

def optimization_inline_nonclosures_without_code(
    abstract     ,
    instructions ,
):
    newInstructions = []
    changed = False
    for index, instruction in enumerate(instructions):
        
        print('AAA', instruction)
        
        if instruction[0] == 'invoke-named-function':
            f = abstract.function(instruction[1])
            if not f.optimizable():
                newInstructions.append(instruction)
            elif any( i[0] == 'invoke-code' for i in f.instructions() ):
                newInstructions.append(instruction)
            else:
                endOfInline = None
                for i in f.instructions():
                    
                    print('BBB', i)
                    
                    if i[0] in [
                        'invoke-named-function',
                        'push-integer',
                        'push-closure',
                        'flow-call-stack',
                        'push-string',
                        'flow-callIf-stack',
                    ]:
                        newInstructions.append(i)
                    elif i[0] in [
                        'set-variable-pop',
                        'push-variable',
                        'set-variable-here',
                        'invoke-variable',
                        'flow-jump-variable-if-stack',
                        'flow-jump-variable',
                        'set-variable-decr',
                        'set-variable-incr',
                    ]:
                        changed = True
                        newInstructions.append( (i[0], '$' + str(index) + i[1], [f.name()] + i[2][1:]) )
                    elif i[0] == 'flow-leaveIf-stack':
                        changed = True
                        if not endOfInline:
                            endOfInline = '$' + str(index)
                        
                        newInstructions.append( ('FLOW-JUMPIF-STACK', endOfInline) )
                    else:
                        raise Exception('unknown instruction: %s' % repr(i))
                
                if endOfInline:
                    newInstructions.append( ('JUMP-TARGET', endOfInline) )
        
        elif instruction[0] in [
            'set-variable-pop',
            'push-variable',
            'push-integer',
            'flow-leaveIf-stack',
            'push-closure',
            'set-variable-decr',
            'set-variable-incr',
            'invoke-code',
            'set-variable-here',
            'flow-jump-variable',
            'flow-callIf-stack',
            'flow-jump-variable-if-stack',
            'invoke-variable',
            'push-string',
            'update-variable',
            'flow-jump-stack',
            'flow-call-stack',
        ]:
            newInstructions.append(instruction)
        else:
            raise Exception('unknown instruction: %s' % repr(instruction))
        
    for i in newInstructions:
        if isinstance(i[0], tuple):
            print('WAT', i)
            
    
    return newInstructions, changed
