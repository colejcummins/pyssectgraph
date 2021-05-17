from dataclasses import dataclass, field
from typing import Set, List
from json import dumps


@dataclass
class Node:
  predecessors: Set[str] = field(default_factory=set)
  successors: Set[str] = field(default_factory=set)
  contents: List[str] = field(default_factory=list)

  def add_pred(self, node_name: str) -> None:
    """Add a node to the set of predecessors"""
    self.predecessors.add(node_name)


  def add_succ(self, node_name: str) -> None:
    """Add a node to the set of successors"""
    self.successors.add(node_name)


  def extend_contents(self, list: List[str]) -> None:
    """Extend contents with a list of strings"""
    self.contents.extend(list)


  def append_contents(self, string: str) -> None:
    """Append a string to contents"""
    self.contents.append(string)


  def to_json(self) -> str:
    return dumps(self)