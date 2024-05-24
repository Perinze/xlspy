import ast
from sys import stderr
from functools import reduce

from lib.name_alloc import NameAllocator, UNALLOC
import lib.config as config
from lib.util import error
from lib.stmt_res import StmtRes

class Typer(ast.NodeVisitor):
    def __init__(self, ast_tree):
        self.ast_tree = ast_tree
        self.name_env : dict = {} # id -> ir_name
        self.type_env : dict = {} # ir_name -> type_name
        self.name_alloc = NameAllocator()
        self.visit(ast_tree)

    def visit_FunctionDef(self, node) -> StmtRes:
        # 递归访问函数的参数和主体
        # TODO iterate possible types in config
        for arg in node.args.args:
            self.visit(arg)
        #print(self.name_env)
        #print(self.type_env)
        self.current_function = node
        self.generic_visit(node)
        return StmtRes()

    # Return(expr? value)
    def visit_Return(self, node: ast.Return) -> StmtRes:
        if node.value == None:
            error("process is not supported")
        ret_id = self.visit(node.value)
        self.current_function.type = self.type_env[ret_id]
        return StmtRes()

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
    def visit_Assign(self, node: ast.Assign) -> StmtRes:
        value_id = self.visit(node.value)
        res = StmtRes()
        for target in node.targets:
            assert self.visit(target) == UNALLOC
            targetName: ast.Name = target
            ir_name = target.name = self.name_env[targetName.id] = self.name_alloc.next_with_name(targetName.id)
            target.type = self.type_env[ir_name] = self.type_env[value_id]
            res.assigned_name_map += [(targetName, ir_name)]
        return res

    # Name(identifier id, expr_context ctx)
    def visit_Name(self, node: ast.Name) -> str:
        if isinstance(node.ctx, ast.Store):
            return UNALLOC
        elif isinstance(node.ctx, ast.Load):
            if self.name_env[node.id] == None:
                error(f"{node.id} undefined")
            else:
                node.name = self.name_env[node.id]
                return node.name
        else:
            error(f"ctx other than Store/Load are not implemented")

    # Constant(constant value, string? kind)
    def visit_Constant(self, node: ast.Constant) -> str:
        node.name = self.name_alloc.next_with_name("literal")
        node.type = self.type_env[node.name] = 'int'
        return node.name

    # If(expr test, stmt* body, stmt* orelse)
    def visit_If(self, node: ast.If) -> StmtRes:
        def acc(a: StmtRes, b: StmtRes) -> StmtRes:
            c = StmtRes()
            c.assigned_names = a.assigned_names + b.assigned_names
            return c
        fst = lambda a: a[0]
        body_res_map = map(self.visit, node.body)
        body_res = reduce(acc, body_res_map)
        #body_res.assigned_names.sort()
        body_assigned_name_map = body_res.assigned_name_map
        body_assigned_name_key = list(map(fst, body_assigned_name_map))
        body_assigned_name_key_id = list(map(lambda x: x.id, body_assigned_name_key))

        if node.orelse != []:
            orelse_res_map = map(self.visit, node.orelse)
            orelse_res = reduce(acc, orelse_res_map)
            #orelse_res.assigned_names.sort()
            orelse_assigned_name_map = orelse_res.assigned_name_map
            orelse_assigned_name_key = list(map(fst, orelse_assigned_name_map))
            orelse_assigned_name_key_id = list(map(lambda x: x.id, orelse_assigned_name_key))

            if body_assigned_name_key_id != orelse_assigned_name_key_id:
                error("different assigned names between branches is not supported")

            node.body_name_map = body_assigned_name_map
            node.orelse_name_map = orelse_assigned_name_map
        else:
            node.body_name_map = body_assigned_name_map
            get_pair_from_env = lambda k: (k, self.name_env[k.id])
            node.orelse_name_map = list(map(get_pair_from_env, body_assigned_name_key))

        def create_sel_name(name: ast.Name) -> tuple[ast.Name, str]:
            id = name.id
            ir_name = self.name_alloc.next_with_name(id)
            self.type_env[ir_name] = self.type_env[self.name_env[id]]
            self.name_env[id] = ir_name
            return (name, ir_name)
        
        # test expr
        self.visit(node.test)
        
        res = StmtRes()
        res.assigned_name_map = node.result_name_map = list(map(create_sel_name, body_assigned_name_key))

        return res
    
    # Compare(expr left, cmpop* ops, expr* comparators)
    def visit_Compare(self, node: ast.Compare) -> str:
        lhs = self.visit(node.left)
        if len(node.ops) != 1:
            error("sequence is not supported")
        rhs = self.visit(node.comparators[0])
        node.name = self.name_alloc.next_with_name("lt")
        node.type = self.type_env[node.name] = self.type_env[lhs]
        return node.name

    # For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
    def visit_For(self, node: ast.For) -> StmtRes:
        if node.orelse != []:
            error("else in for is not supported")
        if not isinstance(node.iter, ast.Call) or node.iter.func.id != 'range':
            error("for-loop without range is not supported")
        if not isinstance(node.iter.args[0], ast.Constant):
            error("dynamic trip count is not supported")
        trip_count = node.iter.args[0].value
        node.trip_count = trip_count
        only_stmt: ast.Assign = node.body[0]
        if len(node.body) != 1:
            error("for-loop body supports exactly one stmt")
        if not isinstance(only_stmt, ast.Assign):
            error("for-loop body should be assignment")
        acc: ast.Name = only_stmt.targets[0]
        acc.prev_name = self.name_env[acc.id]
        self.visit(only_stmt)
        node.name = self.name_alloc.next_with_name('for')
        return StmtRes()
