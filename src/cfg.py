from dataclasses import dataclass, field
from typing import Dict
from .node import Node

@dataclass
class CFG:
  root: str
  cur: str
  nodes: Dict[str, Node]
