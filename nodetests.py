from pycfg.node import Node
from pycfg.cfg import CFG
import unittest


JSON_CFG_OUT = """{
  "root": "a",
  "cur": "a",
  "nodes": {
    "a": {
      "name": "a",
      "start": {
        "line": 0,
        "column": 0
      },
      "end": {
        "line": 0,
        "column": 0
      },
      "parents": [],
      "children": [
        "b"
      ],
      "contents": []
    },
    "b": {
      "name": "b",
      "start": {
        "line": 0,
        "column": 0
      },
      "end": {
        "line": 0,
        "column": 0
      },
      "parents": [
        "a"
      ],
      "children": [],
      "contents": []
    }
  }
}"""

class CFGTest(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(CFGTest, self).__init__(*args, **kwargs)
    self.maxDiff = None

  def test_attach_child(self):
    node_a = Node(name='a')
    cfg = CFG('a', 'a', {'a': node_a})
    node_b = Node(name='b')
    cfg.attach_child(node_b)

    self.assertEqual(len(cfg.nodes), 2)
    self.assertEqual(CFG('a', 'a', {
      'a': Node(name='a', children={'b'}),
      'b': Node(name='b', parents={'a'})
    }), cfg)


  def test_insert_child(self):
    node_a = Node(name='a')
    node_b = Node(name='b')
    node_c = Node(name='c')
    node_d = Node(name='d')
    cfg = CFG('a', 'a', {'a': node_a})

    cfg.attach_child(node_c)
    cfg.attach_child(node_d)
    cfg.insert_child(node_b)

    self.assertEqual(len(cfg.nodes), 4)
    self.assertEqual(CFG('a', 'a', {
      'a': Node(name='a', children={'b'}),
      'b': Node(name='b', parents={'a'}, children={'c', 'd'}),
      'c': Node(name='c', parents={'b'}),
      'd': Node(name='d', parents={'b'})
    }), cfg)


  def test_merge_nodes(self):
    cfg = CFG('a', 'a', {
      'a': Node(name='a', children={'b'}, contents=['hello']),
      'b': Node(name='b', parents={'a'}, children={'c', 'd'}, contents=['world']),
      'c': Node(name='c', parents={'b'}),
      'd': Node(name='d', parents={'b'})
    })

    cfg.merge_nodes('a', 'b')

    self.assertEqual(len(cfg.nodes), 3)
    self.assertEqual(CFG('a', 'a', {
      'a': Node(name='a', children={'c', 'd'}, contents=['hello', 'world']),
      'c': Node(name='c', parents={'a'}),
      'd': Node(name='d', parents={'a'})
    }), cfg)


  def test_to_json_str(self):
    cfg = CFG('a', 'a', {
        'a': Node(name='a', children={'b'}),
        'b': Node(name='b', parents={'a'})
      })

    self.assertEqual(len(cfg.nodes), 2)
    self.assertEqual(JSON_CFG_OUT, cfg.to_json_str())


if __name__ == '__main__':
  unittest.main()