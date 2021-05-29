from pycfg.node import Node
from pycfg.cfg import CFG
from pycfg.cfg_builder import CFGBuilder
from typing import Dict, Any
import json
import ast
import unittest


class CFGBuilderTests(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(CFGBuilderTests, self).__init__(*args, **kwargs)
    self.maxDiff = None


  def test_small(self):
    self.assertEqual(SMALL_JSON, self._simplify_json(self._prog_to_json(SMALL)))


  def test_basic_if(self):
    self.assertEqual(BASIC_IF_JSON, self._simplify_json(self._prog_to_json(BASIC_IF)))


  def test_basic_return(self):
    self.assertEqual(BASIC_RETURN_JSON, self._simplify_json(self._prog_to_json(BASIC_RETURN)))


  def test_if_and_return(self):
    self.assertEqual(IF_AND_RETURN_JSON, self._simplify_json(self._prog_to_json(IF_AND_RETURN)))


  def test_basic_while(self):
    self.assertEqual("", json.dumps(self._simplify_json(self._prog_to_json(BASIC_WHILE))))


  def _prog_to_json(self, prog: str) -> Dict[str, Any]:
    return json.loads(CFGBuilder().build(ast.parse(prog, mode='exec')).to_json_str())


  def _simplify_json(self, json_inp):
    return {
      k: {
        "contents": v["contents"],
        "children": v["children"],
        "parents": v["parents"]
      } for k, v in json_inp['nodes'].items()
    }



SMALL = "x = 1"
SMALL_JSON = {
  "root": {
    "children": {},
    "contents": [
      "x = 1"
    ],
    "parents": {}
  }
}



BASIC_IF = """
x = 1
if x < 4:
  x += 2
x -= 1
"""
BASIC_IF_JSON = {
  "root": {
    "contents": [
      "x = 1"
    ],
    "children": {
      "If_3_0": ""
    },
    "parents": {}
  },
  "If_3_0": {
    "contents": [
      "if x < 4:"
    ],
    "children": {
      "AugAssign_4_2": "True",
      "exit_If_3_0": ""
    },
    "parents": {
      "root": ""
    }
  },
  "AugAssign_4_2": {
    "contents": [
      "x += 2"
    ],
    "children": {
      "exit_If_3_0": ""
    },
    "parents": {
      "If_3_0": "True"
    }
  },
  "exit_If_3_0": {
    "contents": [
      "x -= 1"
    ],
    "children": {},
    "parents": {
      "AugAssign_4_2": "",
      "If_3_0": ""
    }
  }
}



BASIC_RETURN = """
x = 0
return x
x += 1
"""
BASIC_RETURN_JSON = {
  "root": {
    "contents": [
      "x = 0"
    ],
    "children": {
      "Return_3_0": ""
    },
    "parents": {}
  },
  "Return_3_0": {
    "contents": [
      "return x"
    ],
    "children": {},
    "parents": {
      "root": ""
    }
  }
}



IF_AND_RETURN = """
if x > 3:
  if x < 2:
    return 0
  return 1
return 2
"""
IF_AND_RETURN_JSON = {
  "root": {
    "contents": [],
    "children": {
      "If_2_0": ""
    },
    "parents": {}
  },
  "If_2_0": {
    "contents": [
      "if x > 3:"
    ],
    "children": {
      "If_3_2": "True",
      "exit_If_2_0": ""
    },
    "parents": {
      "root": ""
    }
  },
  "If_3_2": {
    "contents": [
      "if x < 2:"
    ],
    "children": {
      "Return_4_4": "",
      "exit_If_3_2": ""
    },
    "parents": {
      "If_2_0": "True"
    }
  },
  "Return_4_4": {
    "contents": [
      "return 0"
    ],
    "children": {},
    "parents": {
      "If_3_2": ""
    }
  },
  "exit_If_3_2": {
    "contents": [],
    "children": {
      "Return_5_2": ""
    },
    "parents": {
      "If_3_2": ""
    }
  },
  "Return_5_2": {
    "contents": [
      "return 1"
    ],
    "children": {},
    "parents": {
      "exit_If_3_2": ""
    }
  },
  "exit_If_2_0": {
    "contents": [],
    "children": {
      "Return_6_0": ""
    },
    "parents": {
      "If_2_0": ""
    }
  },
  "Return_6_0": {
    "contents": [
      "return 2"
    ],
    "children": {},
    "parents": {
      "exit_If_2_0": ""
    }
  }
}



BASIC_WHILE="""
x = 1
while x < 5:
  x += 1
x = 2
"""


if __name__ == '__main__':
  unittest.main()