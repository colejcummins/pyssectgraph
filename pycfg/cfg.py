from dataclasses import dataclass, field
from json import dumps, JSONEncoder
from typing import Dict
from .node import Node, NodeEncoder

@dataclass
class CFG:
  root: str
  cur: str
  nodes: Dict[str, Node]


  def next(self) -> None:
    """Sets the current node to an arbitrary child node"""
    self.cur = self.nodes[self.cur].next()


  def go_to(self, name: str) -> None:
    """Sets the current node to node name"""
    self.cur = name


  def attach_child(self, node: Node) -> None:
    """Add a child node to the current node"""
    self._conditional_add(node)
    self.nodes[self.cur].add_child(node.name)
    self.nodes[node.name].add_parent(self.cur)


  def attach_parent(self, node: Node) -> None:
    """Add a parent node to the current node"""
    self._conditional_add(node)
    self.nodes[self.cur].add_parent(node.name)
    self.nodes[node.name].add_child(self.cur)


  def insert_child(self, node: Node) -> None:
    """Inserts a child node to the current node, replacing node connections from the children to the new parent"""
    self._conditional_add(node)
    self.attach_child(node)

    # For all child nodes of the current node, add the inserted node to the child as a parent, add the child node to
    # the inserted node as a child, then remove the children from the current node
    for child_node in self.nodes[self.cur].children:
      self.nodes[child_node].add_parent(node.name)
      self.nodes[node.name].add_child(child_node)
      self.nodes[child_node].remove_parent(self.cur)


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

    del self.nodes[child]


  def to_json_str(self):
    return dumps(self.__dict__, cls=CFGEncoder, indent=2)


class CFGEncoder(JSONEncoder):
  def default(self, obj):
    print(obj)
    if isinstance(obj, Node):
      return NodeEncoder.default(self, obj)
    return JSONEncoder.default(self, obj)
