from dataclasses import dataclass, field
from typing import Set, List, Dict, Any
from json import dumps, JSONEncoder, JSONDecoder, loads
from ast import AST
from enum import Enum
from dis import Instruction

class Event(Enum):
  """Enum used to describe CFG node transitions"""
  ONFALSE = "False"
  ONTRUE = "True"
  ONCALL = "calls"
  ONBREAK = "break"
  ONCONTINUE = "continue"
  ONYIELD = "yield"
  ONRETURN = "return"
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
  def default_start(node: AST):
    return Location(getattr(node, 'lineno', 1), getattr(node, 'col_offset', 0))


  @staticmethod
  def default_end(node: AST):
    return Location(getattr(node, 'end_lineno', 1), getattr(node, 'end_col_offset', 0))


@dataclass
class Node:
  """Represents a single Node in a Control Flow Graph, with a name, a `Location` start and end
  a dictionary of parent and child nodes and a list of contents.

  Nodes follow a naming convention of `<AST class>_<start line>_<start column>`, for example
  `'If_5_2'`.

  Nodes are json serializable and can be decoded from json, with the methods `to_json_str` and
  `build_node_from_json` respsectively.
  """
  name: str = ''
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
      self.children.remove(node_name)


  def remove_parent(self, node_name: str) -> None:
    """Remove a node from the set of parents"""
    if node_name in self.parents:
      self.parents.remove(node_name)


  def extend_contents(self, list: List[Any]) -> None:
    """Extend contents with a list of strings"""
    self.contents.extend(list)


  def append_contents(self, contents: Any) -> None:
    """Append a string to contents"""
    self.contents.append(contents)
    if isinstance(contents, AST):
      self.end = Location.default_end(contents)
    elif isinstance(contents, Instruction):
      self.end = contents.starts_line or 0


  def next(self) -> str:
    """Returns the name of an arbitrary child node"""
    child = self.children.pop()
    self.children.add(child)
    return child


  def to_json_str(self) -> str:
    """Returns a json representation of the current Node"""
    return dumps(self.__dict__, cls=NodeEncoder, indent=2)



def build_node_from_json(str) -> Node:
  return loads(str, cls=NodeDecoder)


class NodeEncoder(JSONEncoder):
  """Custom JSON Encoder for the Node Class"""
  def default(self, obj):
    if isinstance(obj, Location):
      return obj.__dict__
    if isinstance(obj, Set):
      return list(obj)
    if isinstance(obj, Event):
      return obj.value
    return JSONEncoder.default(self, obj)


class NodeDecoder(JSONDecoder):
  """Custom JSON Decoder for the Node Class"""
  def __init__(self, *args, **kwargs):
    JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)


  def object_hook(self, obj):
    if 'line' in obj and 'column' in obj:
      return Location(obj['line'], obj['column'])
    if 'parents' in obj and 'children' in obj:
      return Node(**obj)
    return obj