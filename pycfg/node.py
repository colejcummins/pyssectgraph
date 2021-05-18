from dataclasses import dataclass, field
from typing import Set, List
from json import dumps


@dataclass
class Node:
  name: str = ''
  parents: Set[str] = field(default_factory=set)
  children: Set[str] = field(default_factory=set)
  contents: List[str] = field(default_factory=list)

  def add_parent(self, node_name: str) -> None:
    """Add a node to the set of predecessors"""
    self.parents.add(node_name)


  def add_child(self, node_name: str) -> None:
    """Add a node to the set of successors"""
    self.children.add(node_name)


  def extend_contents(self, list: List[str]) -> None:
    """Extend contents with a list of strings"""
    self.contents.extend(list)


  def append_contents(self, string: str) -> None:
    """Append a string to contents"""
    self.contents.append(string)


  def next(self) -> str:
    """Returns the name of an arbitrary child node"""
    child = self.children.pop()
    self.children.add(child)
    return child



  def to_json(self) -> str:
    return dumps(self)