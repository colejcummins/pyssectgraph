from dataclasses import dataclass, field
from typing import Dict
from .node import PyssectNode, ControlEvent


@dataclass
class PyssectGraph:
  name: str
  root: str = 'root'
  cur: str = 'root'
  nodes: Dict[str, PyssectNode] = field(default_factory=dict)


  def next(self) -> None:
    """Sets the current node to an arbitrary child node"""
    self.cur = self.nodes[self.cur].next()


  def go_to(self, name: str) -> None:
    """Sets the current node to node name"""
    if name in self.nodes:
      self.cur = name


  def go_to_root(self) -> None:
    self.cur = self.root


  def attach_child(self, node: PyssectNode, event: ControlEvent = ControlEvent.PASS) -> None:
    """Add a child node to the current node"""
    self._conditional_add(node)
    self.nodes[self.cur].add_child(node.name, event)
    self.nodes[node.name].add_parent(self.cur, event)


  def attach_parent(self, node: PyssectNode, event: ControlEvent = ControlEvent.PASS) -> None:
    """Add a parent node to the current node"""
    self._conditional_add(node)
    self.nodes[self.cur].add_parent(node.name, event)
    self.nodes[node.name].add_child(self.cur, event)


  def insert_child(self, node: PyssectNode, event: ControlEvent = ControlEvent.PASS) -> None:
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
    self.nodes[self.cur].add_child(node.name, ControlEvent.PASS)


  def _conditional_add(self, node: PyssectNode) -> None:
    if node.name not in self.nodes:
      self.nodes[node.name] = node


  def merge_nodes(self, parent: PyssectNode, child: PyssectNode) -> None:
    """Merges the two nodes parent and child, attaching all grandchild nodes to the new parent"""
    parent.extend_contents(child.contents)
    parent.end = child.end

    for grandchild_node in child.children:
      parent.add_child(grandchild_node)
      self.nodes[grandchild_node].add_parent(parent.name)
      self.nodes[grandchild_node].remove_parent(child.name)

    parent.remove_child(child)
    del self.nodes[child.name]


  def get_cur(self) -> PyssectNode:
    return self.nodes[self.cur]


  def iter_child_nodes(self):
    """Iterates through all child nodes of the current node"""
    for name in self.nodes[self.cur].children.keys():
      yield self.nodes[name]


  def walk(self):
    """Walks along a control flow graph starting with the current node, yielding all descendant nodes,
    in breadth first order. Extending the queue is done after the each node is yielded, allowing for
    inplace editing of the graph as it is being traversed"""
    from collections import deque
    nodes = deque([self.nodes[self.cur]])
    visited = set()
    while nodes:
      node = nodes.popleft()
      if node.name not in visited:
        self.go_to(node.name)
        visited.add(node.name)
        yield node
        nodes.extend(self.iter_child_nodes())


  def clean_graph(self) -> None:
    self.go_to_root()
    for node in self.walk():
      if self._can_remove(node):
        self._remove_node()


  def _remove_node(self) -> None:
    """Removes the current node from the graph"""

    for parent, p_event in self.nodes[self.cur].parents.items():
      del self.nodes[parent].children[self.cur]
      for child, c_event in self.nodes[self.cur].children.items():
        self.nodes[parent].add_child(child, p_event)
        self.nodes[child].add_parent(parent, c_event)

    for child in self.nodes[self.cur].children.keys():
      del self.nodes[child].parents[self.cur]

    del self.nodes[self.cur]
    self.go_to_root()


  def _can_remove(self, node: PyssectNode) -> bool:
    return (
        len(node.contents) == 0 and
        len(node.parents) <= 1 and
        len(node.children) <= 1 and
        node.name != 'root'
      )
