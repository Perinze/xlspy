import sys
import ast
from functools import reduce

from lib.typer import Typer
from lib.irgen import IRGenerator

def type_inference(ast_tree):
    # 创建Typer实例，并进行类型推导
    typer = Typer(ast_tree)
    return typer.ast_tree

def xlsir_generator(ast_tree):
    generator = IRGenerator(ast_tree)
    return generator.top

def main():
    if len(sys.argv) != 2:
        print("Usage: python ast_parser.py <file_path>")
        return

    file_path = sys.argv[1]
    
    with open(file_path, 'r') as f:
        source_code = f.read()
    
    try:
        tree = ast.parse(source_code)
        print(ast.dump(tree, indent=4))
        typed_tree = type_inference(tree)
        print(ast.dump(typed_tree, indent=4))
        xlsir = xlsir_generator(typed_tree)
        print(xlsir)
    except SyntaxError as e:
        print("SyntaxError:", e)

if __name__ == "__main__":
    main()
