import sys
import ast
from functools import reduce

class NameAllocator:
    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1
        return self.count

    def next_with_name(self, name: str):
        self.count += 1
        return f"{name}.{self.count}"

class Typer(ast.NodeVisitor):
    def __init__(self, ast_tree):
        self.ast_tree = ast_tree
        self.env : dict = {}
        self.name_alloc = NameAllocator()
        self.visit(ast_tree)

    def visit_FunctionDef(self, node) -> None:
        # 递归访问函数的参数和主体
        # TODO iterate possible types in config
        for arg in node.args.args:
            self.visit(arg)
        print(self.env)
        self.current_function = node
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> str:
        ret_id = self.visit(node.value)
        self.current_function.type = self.env[ret_id]
        return ret_id

    def visit_arg(self, node) -> str:
        self.env[node.arg] = node.annotation.id
        node.type = self.env[node.arg]
        node.name = node.arg
        return node.name

    def visit_BinOp(self, node) -> str:
        left = node.left
        right = node.right
        assert self.env[left.id] == self.env[right.id]
        node.type = self.env[left.id]
        node.name = self.name_alloc.next_with_name('add')
        self.env[node.name] = node.type
        return node.name

    def visit_Assign(self, node):
        # 对于赋值语句，简单地将左侧的变量与右侧表达式的类型匹配
        for target in node.targets:
            self.visit(target)
        self.visit(node.value)
        # 这里可以进行类型匹配和推导，根据具体需要进行修改

    def visit_Name(self, node):
        # 这里可以添加对变量名的类型推导逻辑
        return node

    # 还可以实现其他节点类型的visit方法，根据需要进行扩展
    # 注意：需要根据具体情况对各种节点类型进行处理

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

class IRGenerator(ast.NodeVisitor):
    def __init__(self, ast_tree) -> None:
        self.ast_tree = ast_tree
        self.top = IRFunction()
        self.visit(ast_tree)

    def codegen(self) -> IRFunction:
        self.visit(self.ast_tree)
        return self.top

    def visit_FunctionDef(self, node: ast.FunctionDef) -> IRFunction:
        self.top.name = node.name
        self.top.args = map(lambda a: a.arg, node.args.args)
        self.top.ret = node.type
        results = map(self.visit, node.body)
        self.top.body = reduce(lambda x, y: x + y, results)
        return self.top
    
    def visit_Return(self, node: ast.Return) -> list[IROperation]:
        irs : list[IROperation] = self.visit(node.value)
        irs[-1].is_ret = True
        return irs

    def visit_BinOp(self, node: ast.BinOp) -> list[IROperation]:
        left_irs : list[IROperation] = self.visit(node.left)
        right_irs : list[IROperation] = self.visit(node.right)
        binop_irs : list[IROperation] = [IROperation(node.name, 'add', [left_irs[-1].name, right_irs[-1].name])]
        return reduce(lambda x, y: x + y, [left_irs, right_irs, binop_irs])
    
    def visit_Name(self, node: ast.Name) -> list[IROperation]:
        return [IROperation(node.id, 'identity', [node.id])]

def type_inference(ast_tree):
    # 创建Typer实例，并进行类型推导
    typer = Typer(ast_tree)
    return typer.ast_tree

def xlsir_generator(ast_tree):
    generator = IRGenerator(ast_tree)
    return generator.codegen()

def main():
    if len(sys.argv) != 2:
        print("Usage: python ast_parser.py <file_path>")
        return

    file_path = sys.argv[1]
    
    with open(file_path, 'r') as f:
        source_code = f.read()
    
    try:
        tree = ast.parse(source_code)
        typed_tree = type_inference(tree)
        print(ast.dump(typed_tree, indent=4))
        xlsir = xlsir_generator(typed_tree)
        print(xlsir)
    except SyntaxError as e:
        print("SyntaxError:", e)

if __name__ == "__main__":
    main()
