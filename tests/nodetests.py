from pycfg.node import Node
import unittest


class CFGTest(unittest.TestCase):
  pass

def main():
  node = Node('b', {'a'}, {'c', 'd'})
  print(node)

if __name__ == '__main__':
  main()