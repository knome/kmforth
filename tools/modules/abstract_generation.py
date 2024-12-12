
# string string-name "value of string"
# string string-name "value of other string"
# 
# somefunc:
# closure                     parent-function-name
# reserve-trampoline          trampoline-identifier trampoline-target
# reserve-variable            variable-name variable-size
# flow-jump-label             label-name
# flow-conditional-jump-local variable-name
# flow-jump-nonlocal          variable-name
# label                       label-name
# local-get                   variable-name
# invoke                      function-name
# jump                        label-name
# nonlocal-get                variable-name
# push-integer                12345
# push-string                 string-name

# {non,}local-update will be translated into simpler commands
# 
# local-get variable-name
# invoke    function-name
# local-set variable-name

from modules.mangling import unmangle
from modules.abstract_code import AbstractCode

def generate_abstract(
    options       ,
    functions     ,
    usedFunctions ,
    startname     ,
):
    code = AbstractCode(startname)
    
    for functionName in functions:
        if functionName in usedFunctions:
            generate_function(code, functions, functionName, functions[ functionName ])
    
    return code
        
def generate_function(
    code            ,
    functions       ,
    functionName    ,
    functionData    ,
):
    functionBuilder = code.new_function(functionName)
    
    for command in functionData.body_details().commands():
        
        if command.kind() == 'localfn':
            interpret_local_fn(
                functions       = functions       ,
                functionName    = functionName    ,
                functionBuilder = functionBuilder ,
                command         = command         ,
            )
        
        elif command.kind() == 'word':
            functionBuilder.add_instruction('invoke-named-function', command.value())
        
        elif command.kind() == 'integer':
            functionBuilder.add_instruction('push-integer', command.value())
        
        elif command.kind() == 'subfn':
            functionBuilder.add_instruction('push-closure', command.value())
        
        elif command.kind() == 'fnref':
            functionBuilder.add_instruction('push-function', command.value())
            
        elif command.kind() == 'string':
            functionBuilder.add_instruction('push-string', command.value())
            
        elif command.kind() == 'code':
            functionBuilder.add_instruction('invoke-code', command.value())
        
        else:
            raise Exception('unknown command: %s' % repr(command))
    
def interpret_local_fn(
    functions       ,
    functionName    ,
    functionBuilder ,
    command         ,
):
    value = command.value()
    
    if not value:
        raise Exception('implementation error, empty name: %s' % repr(command))
    
    if not value.startswith('$'):
        raise Exception('implementation error, localfn not starting with "$": %s' % repr(command))
    
    if '.' not in value:
        raise Exception('implementation error, bad localfn name: %s' % repr(command))
    
    fore, aft = value.split('.', 1)
    
    if fore == '$':
        interpret_local_flow_fn(
            functionBuilder = functionBuilder ,
            command         = command         ,
            method          = aft             ,
        )
    else:
        interpret_local_variable_fn(
            functions       = functions       ,
            functionName    = functionName    ,
            functionBuilder = functionBuilder ,
            command         = command         ,
            variable        = fore            ,
            method          = aft             ,
        )

def interpret_local_flow_fn(
    functionBuilder ,
    command         ,
    method          ,
):
    if method == 'call':
        functionBuilder.add_instruction('flow-call-stack')
    elif method == 'callIf':
        functionBuilder.add_instruction('flow-callIf-stack')
    elif method == 'jump':
        functionBuilder.add_instruction('flow-jump-stack')
    elif method == 'jumpIf':
        functionBuilder.add_instruction('flow-jumpIf-stack')
    elif method == 'leaveIf':
        functionBuilder.add_instruction('flow-leaveIf-stack')
    elif method == 'noopt':
        functionBuilder.mark_do_not_optimize()
    else:
        raise Exception('unknown local function: %s' % repr( command ))

def interpret_local_variable_fn(
    functions       ,
    functionName    ,
    functionBuilder ,
    command         ,
    variable        ,
    method          ,
):
    path = find_variable(
        functions    = functions    ,
        functionName = functionName ,
        variable     = variable     ,
    )
    
    if len(path) > 1:
        functionBuilder.mark_is_closure()
    
    if method == 'get':
        functionBuilder.add_instruction('push-variable', variable, path)
    elif method == 'set':
        functionBuilder.add_instruction('set-variable-pop', variable, path)
    elif method == 'here':
        functionBuilder.add_instruction('set-variable-here', variable, path)
    elif method == 'addr':
        functionBuilder.add_instruction('push-variable-addr', variable, path)
    elif method == 'incr':
        functionBuilder.add_instruction('set-variable-incr', variable, path)
    elif method == 'decr':
        functionBuilder.add_instruction('set-variable-decr', variable, path)
    elif method == 'jump':
        functionBuilder.add_instruction('flow-jump-variable', variable, path)
    elif method == 'jumpIf':
        functionBuilder.add_instruction('flow-jump-variable-if-stack', variable, path)
    elif method == 'update':
        functionBuilder.add_instruction('update-variable', variable, path)
    elif method == 'call':
        functionBuilder.add_instruction('invoke-variable', variable, path)
    elif method == 'copy':
        functionBuilder.add_instruction('set-variable-copy', variable, path)
    else:
        raise Exception('unknown local variable function: %s' % repr(command))

def find_variable(
    functions    ,
    functionName ,
    variable     ,
):
    c    = functionName
    path = [c]
    while True:
        cf = functions[c]
        
        found = [
            v[0]
            for v in cf.body().localvars()
            if v[0] == variable
        ]
        
        if found:
            return path
        elif p := cf.parent():
            path.append(p)
            c = p
        else:
            raise Exception(
                'unresolve variable %s in function %s' % (
                    repr(variable)        ,
                    unmangle(functionName) ,
                )
            )
