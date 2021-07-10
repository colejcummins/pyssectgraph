from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
from dis import Instruction
import ast


class Event(Enum):
  """Enum used to describe CFG node transitions"""
  ONFALSE = "False"
  ONTRUE = "True"
  ONCALL = "calls"
  ONBREAK = "break"
  ONCONTINUE = "continue"
  ONYIELD = "yield"
  ONRETURN = "return"
  ONEXCEPTION = "excepts"
  ONFINALLY = "finally"
  ONTRY = "try"
  PASS = ""


@dataclass
class Location:
  """A class that describes a single location in a file, with line and column fields.
  As described by the python AST class, `line` is one indexed whereas `column` is
  zero indexed
  """
  line: int = 0
  column: int = 0

  @staticmethod
  def default_start(node: ast.AST):
    return Location(getattr(node, 'lineno', 1), getattr(node, 'col_offset', 0))


  @staticmethod
  def default_end(node: ast.AST):
    return Location(getattr(node, 'end_lineno', 1), getattr(node, 'end_col_offset', 0))


@dataclass
class Node:
  """Represents a single Node in a Control Flow Graph, with a name, a `Location` start and end,
  a dictionary of parent and child nodes, and a list of contents.

  AST nodes follow a naming convention of `<AST class>_<start line>_<start column>`, for example
  `'If_5_2'`.
  """
  name: str = 'root'
  start: Location = field(default_factory=Location)
  end: Location = field(default_factory=Location)
  parents: Dict[str, Event] = field(default_factory=dict)
  children: Dict[str, Event] = field(default_factory=dict)
  contents: List[Any] = field(default_factory=list)


  def add_parent(self, node_name: str, event: Event) -> None:
    """Add a node to the set of parents"""
    self.parents[node_name] = event


  def add_child(self, node_name: str, event: Event) -> None:
    """Add a node to the set of children"""
    self.children[node_name] = event


  def remove_child(self, node_name: str) -> None:
    """Remove a node from the set of children"""
    if node_name in self.children:
      del self.children[node_name]


  def remove_parent(self, node_name: str) -> None:
    """Remove a node from the set of parents"""
    if node_name in self.parents:
      del self.parents[node_name]


  def extend_contents(self, list: List[Any]) -> None:
    """Extend contents with a list of strings"""
    self.contents.extend(list)


  def append_contents(self, contents: Any) -> None:
    """Append a string to contents"""
    self.contents.append(contents)
    if isinstance(contents, ast.AST):
      self.end = Location.default_end(contents)
    elif isinstance(contents, Instruction):
      self.end = contents.starts_line or 0


  def next(self) -> str:
    """Returns the name of an arbitrary child node"""
    child = self.children.pop()
    self.children.add(child)
    return child
