import ast

class StmtRes:
    def __init__(self) -> None:
        self.assigned_name_map : list[ast.Name] = []