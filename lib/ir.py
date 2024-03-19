
class IROperation:
    def __init__(self, name, operation, args, is_ret=False):
        self.name = name
        self.operation = operation
        self.args = args
        self.is_ret = is_ret

    def __repr__(self) -> str:
        return f"{self.name} = {self.operation}({', '.join(self.args)})"

class IRFunction:
    def __init__(self, name, args, ret, body=[], top=True) -> None:
        self.name = name
        self.args = args
        self.ret = ret
        self.body = body
        self.top = top

    def __init__(self) -> None:
        self.name = "untitled"
        self.args = []
        self.ret = "no_ret"
        self.body = []
        self.top = True
    
    def __repr__(self) -> str:
        h = f"{'top ' if self.top else ''}fn {self.name}({', '.join(self.args)}) -> {self.ret} {'{'}"
        b = "\n".join(map(lambda ir: "  " + repr(ir), self.body))
        e = '}'
        return "\n".join([h, b, e])