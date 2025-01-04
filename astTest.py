import ast

print(ast.dump(ast.parse('x = 1'), indent=4))
