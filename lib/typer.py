import ast

from lib.name_alloc import NameAllocator

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
        # TODO type it
        for target in node.targets:
            self.visit(target)
        self.visit(node.value)

    def visit_Name(self, node):
        # TODO type it
        return node