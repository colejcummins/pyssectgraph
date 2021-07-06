from .node import Node, Event, Location
from .cfg import CFG
from typing import Set, Dict
import ast
import json


def cfg_loads(str: str):
  """Takes in a JSON string and returns a corresponding Control Flow Graph, Node, or Location"""
  def object_hook(obj):
    # TODO implement strict rules for json conversion, with errors
    if 'name' in obj and 'cur' in obj and 'root' in obj:
      return CFG(**obj)
    if 'line' in obj and 'column' in obj:
      return Location(obj['line'], obj['column'])
    if 'parents' in obj and 'children' in obj:
      return Node(**obj)
    return obj
  return json.loads(str, object_hook=object_hook)


def _ast_no_recurse(node: ast.AST) -> ast.AST:
  """Turns an AST node with nested nodes into a flattened node for string representation."""
  l = ast.Expr(value=ast.Ellipsis())
  if hasattr(node, 'body'):
    node.__setattr__('body', [l])
  if hasattr(node, 'orelse'):
    node.__setattr__('orelse', [l] if node.orelse else [])
  return node


def cfg_dumps(obj, indent: int=2, simple: bool = False) -> str:
  """Returns a json string representation of the Control Flow Graph"""
    # TODO implement a simplified json for for the CFG Encoder
  def default(obj):
    if type(obj) in [Node, CFG, Location]:
      if simple and isinstance(obj, Node):
        return {
          'contents': obj['contents'],
          'children': obj['children'],
          'parents': obj['parents']
        }
      return obj.__dict__
    if isinstance(obj, Set):
      return list(obj)
    if isinstance(obj, Event):
      return obj.value
    if isinstance(obj, ast.AST):
      return ast.unparse(_ast_no_recurse(obj))
    return json.JSONEncoder.default(obj)
  return json.dumps(obj, default=default, indent=indent)