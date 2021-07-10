import ast
import sys
import dis
import pdb
import builtins
import inspect
import timeit
import functools
from types import BuiltinFunctionType
import types
from typing import Dict
from pycfg import builds, cfg_dumps, CFG
import json

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

SAMPLE_PROG="""
def fib(n):
  if n == 0 or n == 1:
    return n
  return fib(n - 1) + fib(n - 2)
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


EXAMPLE_PROGRAM="""
def fib(n):
  if n == 0 or n == 1:
    return n
  return fib(n - 1) + fib(n - 2)

def main():
  print(fib(20))

if __name__ == '__main__':
  main()
"""


def fib(n):
  if n == 0 or n == 1:
    return n
  return fib(n - 1) + fib(n - 2)


def test_loop(n):
  while n < 5:
    if n == 4:
      continue
    n += 2


test_loop_str = """
def test_loop(n):
  while n < 5:
    if n == 4:
      continue
    n += 2
"""

BASIC_TRY = """
try:
  x += 1
except Exception as e:
  print(x)
"""


TRY_WITH_FINALLY_ELSE = """
try:
  x += 1
except ArithmeticError:
  print("arithmetic")
except Exception:
  print("exception")
else:
  print("else")
finally:
  print("finally")
"""


def test_if_exp(n):
  pdb.set_trace()
  return n if n < 5 else n - 1

def build_from_file(file_name: str, clean) -> Dict[str, CFG]:
  d = {}
  with open(file_name, 'r') as f:
    prog = ''.join(f.readlines())
    d = builds(prog, clean)
  return d


def sum_lengths(cfg) -> int:
  return functools.reduce(lambda s, k_v: s + len(k_v[1].nodes), cfg.items(), 0)


def main():
  print(inspect.getsource(sys._getframe()))
  print(cfg_dumps(builds(TRY_WITH_FINALLY_ELSE, True), simple=True))



def is_user_function(name: str) -> bool:
  return name not in builtins.__dict__


if __name__ == '__main__':
  main()