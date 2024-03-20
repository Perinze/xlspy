import ast
from functools import reduce

from lib.ir import *

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
        return [IROperation(node.name, 'identity', [node.id])]

    def visit_Constant(self, node: ast.Constant) -> list[IROperation]:
        return [IROperation(node.name, 'literal', [str(node.value)])]

    def visit_Assign(self, node: ast.Assign) -> list[IROperation]:
        value_irs : list[IROperation] = self.visit(node.value)
        f = lambda target: IROperation(target.name, 'identity', [value_irs[-1].name])
        assign_irs : list[IROperation] = list(map(f, node.targets))
        return value_irs + assign_irs