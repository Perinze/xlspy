import ast
from functools import reduce

from lib.ir import *

Name = str
ExprResult = (list[IROperation], Name)
StmtResult = list[IROperation]

class IRGenerator(ast.NodeVisitor):
    def __init__(self, ast_tree) -> None:
        self.ast_tree = ast_tree
        self.node_env : dict[Name, IROperation] = {}
        self.top = IRFunction()
        self.visit(ast_tree)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> IRFunction:
        self.top.name = node.name
        self.top.args = map(lambda a: a.arg, node.args.args)
        self.top.ret = node.type
        results = map(self.visit, node.body)
        self.top.body = reduce(lambda x, y: x + y, results)
        return self.top
    
    def visit_Return(self, node: ast.Return) -> StmtResult:
        (irs, name) = self.visit(node.value)
        self.node_env[name].is_ret = True
        return irs

    def visit_BinOp(self, node: ast.BinOp) -> ExprResult:
        (left_irs, left_name) = self.visit(node.left)
        (right_irs, right_name) = self.visit(node.right)
        binop_irs: list[IROperation] = [IROperation(node.name, 'add', [left_name, right_name])]
        self.node_env[node.name] = binop_irs[0]
        irs = reduce(lambda x, y: x + y, [left_irs, right_irs, binop_irs])
        return (irs, node.name)
    
    def visit_Name(self, node: ast.Name) -> ExprResult:
        return ([], node.name)

    def visit_Constant(self, node: ast.Constant) -> ExprResult:
        irs = [IROperation(node.name, 'literal', [str(node.value)])]
        self.node_env[node.name] = irs[0]
        return (irs, node.name)

    def visit_Assign(self, node: ast.Assign) -> StmtResult:
        (value_irs, value_name) = self.visit(node.value)
        def f(target):
            ir = IROperation(target.name, 'identity', [value_name])
            self.node_env[target.name] = ir
            return ir
        assign_irs : list[IROperation] = list(map(f, node.targets))
        return value_irs + assign_irs

    def visit_If(self, node: ast.If) -> StmtResult:
        acc = lambda a, b: a + b
        body_ir = reduce(acc, map(self.visit, node.body), [])
        orelse_ir = reduce(acc, map(self.visit, node.orelse), [])
        node.body_name_map.sort()
        node.orelse_name_map.sort()
        node.result_name_map.sort()
        (cond_ir, cond_name) = self.visit(node.test)
        sel_irs = []
        for i in range(len(node.body_name_map)):
            ir = IROperation(node.result_name_map[i][1], 'sel', [cond_name, f"cases=[{node.body_name_map[i][1]}, {node.orelse_name_map[i][1]}]"])
            sel_irs += [ir]
            self.node_env[node.result_name_map[i][1]] = ir
        return body_ir + orelse_ir + cond_ir + sel_irs
    
    def visit_Compare(self, node: ast.Compare) -> ExprResult:
        (lhs_ir, lhs_name) = self.visit(node.left)
        (rhs_ir, rhs_name) = self.visit(node.comparators[0])
        cmp_ir = [IROperation(node.name, "eq", [lhs_name, rhs_name])]
        return (lhs_ir + rhs_ir + cmp_ir, node.name)