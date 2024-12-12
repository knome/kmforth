
class AbstractCode:
    def __init__(
        self      ,
        startname ,
    ):
        self._startname = startname
        self._functions = {}
        return
    
    def startname(
        self ,
    ):
        return self._startname
    
    def functions(
        self ,
    ):
        return self._functions.values()
    
    def function(
        self         ,
        functionName ,
    ):
        return self._functions[functionName]
    
    def dump(
        self ,
    ):
        for function in self.functions():
            print('name', function.name())
            print('optimizable', function.optimizable())
            print('is-closure', function.is_closure())
            print('instructions:')
            for instruction in function.instructions():
                print(' ', instruction)
            print()
    
    def new_function(
        self         ,
        functionName ,
    ):
        if functionName in self._functions:
            raise Exception('implementation error, repeat function: %s' % repr(functionName))
        else:
            cf = AbstractFunctionBuilder(
                functionName ,
            )
            
            self._functions[functionName] = cf
            
            return cf

class AbstractFunctionBuilder:
    def __init__(
        self         ,
        functionName ,
    ):
        self._functionName   = functionName
        self._instructions   = []
        self._trampolines    = []
        self._localVariables = []
        self._optimizable    = True
        self._isClosure      = False
        return
    
    def name(
        self ,
    ):
        return self._functionName
    
    def instructions(
        self ,
    ):
        return self._instructions
    
    def optimizable(
        self ,
    ):
        return self._optimizable
    
    def is_closure(
        self ,
    ):
        return self._isClosure
    
    def mark_is_closure(
        self ,
    ):
        self._isClosure = True
    
    def mark_do_not_optimize(
        self ,
    ):
        self._optimizable = False
    
    def add_instruction(
        self  ,
        *args
    ):
        self._instructions.append(args)
        return
