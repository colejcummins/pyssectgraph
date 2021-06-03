import ast
import sys
import dis
import pdb
from pycfg import build_cfg_from_json

PROGRAM = """
x = 4
for j in i:
  for k in j:
    x += 1
x += 2
"""

SIMPLE_IF="""
x = (4 + 5) - (10 / 2)
"""

EXAMPLE_NODE = """{
  "name": "a",
  "start": {
    "line": 0,
    "column": 0
  },
  "end": {
    "line": 0,
    "column": 0
  },
  "parents": {},
  "children": {
    "b": ""
  },
  "contents": []
}"""


EXAMPLE_CFG = """{
  "name": "test",
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
      "parents": {},
      "children": {
        "b": ""
      },
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
      "parents": {
        "a": ""
      },
      "children": {},
      "contents": []
    }
  }
}"""


WALKING_CFG = """{
"name": "test",
"root": "root",
"cur": "root",
"nodes": {
  "root": {
    "name": "root",
    "contents": [],
    "children": {
      "While_2_0": ""
    },
    "parents": {}
  },
  "While_2_0": {
    "name": "While_2_0",
    "contents": [
      "while x < 10:"
    ],
    "children": {
      "If_3_2": "True",
      "exit_While_2_0": ""
    },
    "parents": {
      "root": "",
      "Continue_4_4": "continue",
      "exit_If_5_2": ""
    }
  },
  "If_3_2": {
    "name": "If_3_2",
    "contents": [
      "if x == 5:"
    ],
    "children": {
      "Continue_4_4": "",
      "exit_If_3_2": ""
    },
    "parents": {
      "While_2_0": "True"
    }
  },
  "Continue_4_4": {
    "name": "Continue_4_4",
    "contents": [
      "continue"
    ],
    "children": {
      "While_2_0": "continue"
    },
    "parents": {
      "If_3_2": ""
    }
  },
  "exit_If_3_2": {
    "name": "exit_If_3_2",
    "contents": [],
    "children": {
      "If_5_2": "True"
    },
    "parents": {
      "If_3_2": ""
    }
  },
  "If_5_2": {
    "name": "If_5_2",
    "contents": [
      "if x == 1:"
    ],
    "children": {
      "AugAssign_6_4": "True",
      "exit_If_5_2": ""
    },
    "parents": {
      "exit_If_3_2": "True"
    }
  },
  "AugAssign_6_4": {
    "name": "AugAssign_6_4",
    "contents": [
      "x += 2"
    ],
    "children": {
      "Break_7_4": ""
    },
    "parents": {
      "If_5_2": "True"
    }
  },
  "Break_7_4": {
    "name": "Break_7_4",
    "contents": [
      "break"
    ],
    "children": {
      "exit_While_2_0": "break"
    },
    "parents": {
      "AugAssign_6_4": ""
    }
  },
  "exit_While_2_0": {
    "name": "exit_While_2_0",
    "contents": [
      "x += 2"
    ],
    "children": {},
    "parents": {
      "Break_7_4": "break",
      "While_2_0": ""
    }
  },
  "exit_If_5_2": {
    "name": "exit_If_5_2",
    "contents": [
      "x += 1"
    ],
    "children": {
      "While_2_0": ""
    },
    "parents": {
      "If_5_2": ""
    }
  }
}
}"""


def fib(n):
  if n == 0 or n == 1:
    return n
  return fib(n - 1) + fib(n - 2)


def main():
  cfg = build_cfg_from_json(WALKING_CFG)

  for node in cfg.walk():
    print(node)

if __name__ == '__main__':
  main()