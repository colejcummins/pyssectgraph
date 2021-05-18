from pycfg.node import Node
from pycfg.cfg import CFG
import unittest


class CFGTest(unittest.TestCase):
  pass

def main():
  node_a = Node(name='a', parents={}, children={'b'})
  node_b = Node(name='b')
  node_c = Node(name='c')
  node_d = Node(name='d')

  cfg = CFG('a', 'a', {'a': node_a})
  cfg.attach_child(node_b)
  cfg.go_to('b')
  cfg.attach_child(node_c)
  cfg.attach_child(node_d)

  print(cfg.to_json_str())

if __name__ == '__main__':
  main()