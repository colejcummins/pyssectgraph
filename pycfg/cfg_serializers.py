from .node import Node, Event, Location
from .cfg import CFG
from typing import Set, Dict
import ast
import json


class CFGEncoder(json.JSONEncoder):
  """Custom JSON Encoder for the Node Class"""
  def default(self, obj):
    if type(obj) in [Node, CFG, Location]:
      return obj.__dict__
    if isinstance(obj, Set):
      return list(obj)
    if isinstance(obj, Event):
      return obj.value
    if isinstance(obj, ast.AST):
      return self._ast_no_recurse(obj)
    return json.JSONEncoder.default(self, obj)


  def _ast_no_recurse(self, node: ast.AST) -> str:
    """Turns an AST node with nested nodes into a flattened node for string representation."""
    l = ast.Expr(value=ast.Ellipsis())
    if hasattr(node, 'body'):
      node.__setattr__('body', [l])
    if hasattr(node, 'orelse'):
      node.__setattr__('orelse', [l] if node.orelse else [])
    return ast.unparse(node)


class CFGDecoder(json.JSONDecoder):
  """Custom JSON Decoder for the CFG Class"""
  def __init__(self, *args, **kwargs):
    json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)


  def object_hook(self, obj):
    # TODO implement strict rules for json conversion, with errors
    if 'name' in obj and 'cur' in obj and 'root' in obj:
      return CFG(**obj)
    if 'line' in obj and 'column' in obj:
      return Location(obj['line'], obj['column'])
    if 'parents' in obj and 'children' in obj:
      return Node(**obj)
    return obj


def cfg_loads(str: str):
  """Takes in a JSON string and returns a corresponding Control Flow Graph, Node, or Location"""
  return json.loads(str, cls=CFGDecoder)


def cfg_dumps(obj, indent: int=2) -> str:
  """Returns a json string representation of the Control Flow Graph"""
  return json.dumps(obj, cls=CFGEncoder, indent=indent)