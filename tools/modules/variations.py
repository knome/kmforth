
class Variations:
    def __init__(
        self  ,
        value ,
    ):
        self._values = [ value ]
    
    def variations(
        self ,
    ):
        for value in self._values:
            yield value
