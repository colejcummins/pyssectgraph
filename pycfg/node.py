from dataclasses import dataclass, field
from typing import Set, List, Dict
from json import dumps, JSONEncoder
from ast import stmt, expr, AST
from enum import Enum

class Event(Enum):
  ONFALSE = "False"
  ONTRUE = "True"
  ONCALL = "calls"
  ONBREAK = "break"
  CONTINUE = ""


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
  parents: Dict[str, Event] = field(default_factory=dict)
  children: Dict[str, Event] = field(default_factory=dict)
  contents: List[stmt | expr] = field(default_factory=list)


  def add_parent(self, node_name: str, event: Event) -> None:
    """Add a node to the set of parents"""
    self.parents[node_name] = event


  def add_child(self, node_name: str, event: Event) -> None:
    """Add a node to the set of children"""
    self.children[node_name] = event


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
    if isinstance(obj, Event):
      return obj.value
    return JSONEncoder.default(self, obj)