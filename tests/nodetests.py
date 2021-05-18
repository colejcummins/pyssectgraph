from pycfg.node import Node
import unittest


class CFGTest(unittest.TestCase):
  pass

def main():
  node = Node(name='b', parents={'a'}, children={'c', 'd'})
  print(node)

if __name__ == '__main__':
  main()