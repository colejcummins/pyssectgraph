from ast import parse, dump, iter_child_nodes, unparse, Name, Load, AugAssign, Store, Add, Constant, If
from cfg_builder import CFGBuilder

PROGRAM = """
x = 4
for j in i:
  for k in j:
    x += 1
x += 2
"""

SIMPLE_IF="""
if x < 4:
  x += 1
"""


def fib(n):
  if n == 0 or n == 1:
    return n
  return fib(n - 1) + fib(n - 2)


def main():
  builder = CFGBuilder()

  print(builder.build(parse(SIMPLE_IF, mode='exec')))
if __name__ == '__main__':
  main()