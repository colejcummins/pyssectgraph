from dataclasses import dataclass, field
from typing import Dict
from .node import Node

@dataclass
class CFG:
  root: str
  cur: str
  nodes: Dict[str, Node]

  def next(self) -> None:
    """Sets the current node to an arbitrary child node"""
    self.cur = self.nodes[self.cur].next()


  def go_to(self, name: str):
    """Sets the current node to node name"""
    self.cur = name


