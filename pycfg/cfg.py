from dataclasses import dataclass, field
from typing import Dict, Tuple, Set
from .node import Node, NodeEncoder, Location, Event, NodeDecoder
import ast
import astor
import json

@dataclass
class CFG:
  name: str
  root: str = 'root'
  cur: str = 'root'
  visited: Set[str] = field(default_factory=set)
  nodes: Dict[str, Node] = field(default_factory=dict)


  def next(self) -> None:
    """Sets the current node to an arbitrary child node"""
    self.cur = self.nodes[self.cur].next()


  def go_to(self, name: str) -> None:
    """Sets the current node to node name"""
    if name in self.nodes:
      self.cur = name


  def attach_child(self, node: Node, event: Event = Event.PASS) -> None:
    """Add a child node to the current node"""
    self._conditional_add(node)
    self.nodes[self.cur].add_child(node.name, event)
    self.nodes[node.name].add_parent(self.cur, event)


  def attach_parent(self, node: Node, event: Event = Event.PASS) -> None:
    """Add a parent node to the current node"""
    self._conditional_add(node)
    self.nodes[self.cur].add_parent(node.name, event)
    self.nodes[node.name].add_child(self.cur, event)


  def insert_child(self, node: Node, event: Event = Event.PASS) -> None:
    """Inserts a child node to the current node, replacing node connections from the children to the new parent"""
    self._conditional_add(node)
    self.attach_child(node)

    # For all child nodes of the current node, add the inserted node to the child as a parent, add the child node to
    # the inserted node as a child, then remove the children from the current node
    for child_name in self.nodes[self.cur].children.keys():
      if child_name != node.name:
        self.nodes[child_name].add_parent(node.name, event)
        self.nodes[node.name].add_child(child_name, event)
        self.nodes[child_name].remove_parent(self.cur)

    self.nodes[self.cur].children.clear()
    self.nodes[self.cur].add_child(node.name, Event.PASS)


  def _conditional_add(self, node: Node) -> None:
    if node.name not in self.nodes:
      self.nodes[node.name] = node


  def merge_nodes(self, parent: str, child: str) -> None:
    """Merges the two nodes parent and child, attaching all grandchild nodes to the new parent"""
    self.nodes[parent].extend_contents(self.nodes[child].contents)
    self.nodes[parent].end = self.nodes[child].end

    for grandchild_node in self.nodes[child].children:
      self.nodes[parent].add_child(grandchild_node)
      self.nodes[grandchild_node].add_parent(parent)
      self.nodes[grandchild_node].remove_parent(child)

    self.nodes[parent].remove_child(child)
    del self.nodes[child]


  def get_cur(self) -> Node:
    return self.nodes[self.cur]


  def to_json_str(self) -> str:
    """Returns a json string representation of the cfg"""
    return json.dumps(self.__dict__, cls=CFGEncoder, indent=2)


  def iter_child_nodes(self):
    """Iterates through all child nodes of the current node"""
    for name, _ in self.nodes[self.cur].children.items():
      yield self.nodes[name]


  def walk(self):
    """Walks along a control flow graph starting with the current node, yielding all child nodes, in BFS order"""
    from collections import deque
    nodes = deque([self.nodes[self.cur]])
    visited = set()
    while nodes:
      node = nodes.popleft()
      if node.name not in visited:
        self.go_to(node.name)
        visited.add(node.name)
        nodes.extend(self.iter_child_nodes())
        yield node


def build_from_json(str) -> CFG:
  """Takes in a JSON string and returns a corresponding Control Flow Graph"""
  return json.loads(str, cls=CFGDecoder)


class CFGEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Node):
      return obj.__dict__

    if isinstance(obj, ast.AST):
      return self._ast_no_recurse(obj)
    return NodeEncoder.default(self, obj)


  def _ast_no_recurse(self, node: ast.AST) -> str:
    if type(node) in [ast.While, ast.If]:
      return ast.unparse(node.__class__(node.test, [], []))
    if isinstance(node, ast.For):
      return ast.unparse(ast.For(node.target, node.iter, [], []))
    return ast.unparse(node)


class CFGDecoder(json.JSONDecoder):
  def __init__(self, *args, **kwargs):
    json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)


  def object_hook(self, obj):
    if 'name' in obj and 'cur' in obj and 'root' in obj:
      return CFG(**obj)
    return NodeDecoder.object_hook(self, obj)