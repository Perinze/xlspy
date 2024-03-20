import ast
from sys import stderr

from lib.name_alloc import NameAllocator, UNALLOC
import lib.config as config
from lib.util import error

class Typer(ast.NodeVisitor):
    def __init__(self, ast_tree):
        self.ast_tree = ast_tree
        self.name_env : dict = {} # id -> ir_name
        self.type_env : dict = {} # ir_name -> type_name
        self.name_alloc = NameAllocator()
        self.visit(ast_tree)

    def visit_FunctionDef(self, node) -> None:
        # 递归访问函数的参数和主体
        # TODO iterate possible types in config
        for arg in node.args.args:
            self.visit(arg)
        print(self.name_env)
        print(self.type_env)
        self.current_function = node
        self.generic_visit(node)

    # Return(expr? value)
    def visit_Return(self, node: ast.Return) -> None:
        if node.value == None:
            error("process is not supported")
        ret_id = self.visit(node.value)
        self.current_function.type = self.type_env[ret_id]

    # arg = (identifier arg, expr? annotation, string? type_comment)
    #        attributes (int lineno, int col_offset, int? end_lineno,
    #        int? end_col_offset)
    def visit_arg(self, node: ast.arg) -> None:
        name = node.name = self.name_env[node.arg] = node.arg
        if node.annotation == None:
            node.type = self.type_env[name] = config.default_types[0]
        else:
            node.type = self.type_env[name] = node.annotation.id

    # BinOp(expr left, operator op, expr right)
    def visit_BinOp(self, node: ast.BinOp) -> str:
        left_name = self.visit(node.left)
        right_name = self.visit(node.right)
        assert self.type_env[left_name] == self.type_env[right_name]
        node.name = self.name_alloc.next_with_name('add')
        node.type = self.type_env[node.name] = self.type_env[left_name]
        return node.name

    # Assign(expr* targets, expr value, string? type_comment)
    def visit_Assign(self, node: ast.Assign) -> None:
        value_id = self.visit(node.value)
        for target in node.targets:
            assert self.visit(target) == UNALLOC
            targetName: ast.Name = target
            ir_name = target.name = self.name_env[targetName.id] = self.name_alloc.next_with_name(targetName.id)
            self.type_env[ir_name] = self.type_env[value_id]

    # Name(identifier id, expr_context ctx)
    def visit_Name(self, node: ast.Name) -> str:
        if isinstance(node.ctx, ast.Store):
            return UNALLOC
        elif isinstance(node.ctx, ast.Load):
            if self.name_env[node.id] == None:
                error(f"{node.id} undefined")
            else:
                return self.name_env[node.id]
        else:
            error(f"ctx other than Store/Load are not implemented")

    # Constant(constant value, string? kind)
    def visit_Constant(self, node: ast.Constant) -> str:
        node.name = self.name_alloc.next_with_name("literal")
        node.type = self.type_env[node.name] = 'int'
        return node.name