from dataclasses import dataclass, field
from typing import Set, List, Dict
from json import dumps, JSONEncoder
from ast import stmt, expr, AST


@dataclass
class Location:
  line: int = 0
  column: int = 0

  @staticmethod
  def default_start(node: AST):
    return Location(getattr(node, 'lineno', 0), getattr(node, 'col_offset', 0))


  @staticmethod
  def default_end(node: AST):
    return Location(getattr(node, 'end_lineno', 0), getattr(node, 'end_col_offset', 0))


@dataclass
class Node:
  name: str = ''
  start: Location = field(default_factory=Location)
  end: Location = field(default_factory=Location)
  parents: Set[str] = field(default_factory=set)
  children: Set[str] = field(default_factory=set)
  contents: List[stmt | expr] = field(default_factory=list)


  def add_parent(self, node_name: str) -> None:
    """Add a node to the set of parents"""
    self.parents.add(node_name)


  def add_child(self, node_name: str) -> None:
    """Add a node to the set of children"""
    self.children.add(node_name)


  def remove_child(self, node_name: str) -> None:
    """Remove a node from the set of children"""
    if node_name in self.children:
      self.children.remove(node_name)


  def remove_parent(self, node_name: str) -> None:
    """Remove a node from the set of parents"""
    if node_name in self.parents:
      self.parents.remove(node_name)


  def extend_contents(self, list: List[stmt | expr]) -> None:
    """Extend contents with a list of strings"""
    self.contents.extend(list)


  def append_contents(self, contents: stmt | expr) -> None:
    """Append a string to contents"""
    self.contents.append(contents)
    self.end = Location.default_end(contents)


  def next(self) -> str:
    """Returns the name of an arbitrary child node"""
    child = self.children.pop()
    self.children.add(child)
    return child


  def to_json_str(self) -> str:
    """Returns a json representation of the current Node"""
    return dumps(self.__dict__, cls=NodeEncoder, indent=2)


# Custom JSON Encoder for the Node Class
class NodeEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Location):
      return obj.__dict__
    if isinstance(obj, Set):
      return list(obj)
    return JSONEncoder.default(self, obj)