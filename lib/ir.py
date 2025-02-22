from lib.type import type_map

class IROperation:
    def __init__(self, name, type, operation, args, is_ret=False):
        self.name = name
        self.type = type
        self.operation = operation
        self.args = args
        self.is_ret = is_ret

    def __repr__(self) -> str:
        return f"{'ret ' if self.is_ret else ''}{self.name}: {type_map[self.type]} = {self.operation}({', '.join(self.args)})"

class IRFunction:
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