from cfg import CFG
from node import Node, Location
from typing import Any, List
from ast import NodeVisitor, AST, iter_child_nodes, stmt, expr


class CFGBuilder(NodeVisitor):
  cfg: CFG
  current_block: List[stmt | expr]


  def __init__(self):
    super().__init__()


  def build(self, node: AST) -> CFG:
    self.cfg = CFG('test', 'root', 'root', {'root': Node('root')})
    self.current_block = []
    self.visit(node)
    return self.cfg


  def traverse_function(self, stmts: List[stmt]) -> None:
    for stmt in stmts:
      self.visit(stmt)


  def visit_If(self, node: AST) -> Any:
    cfg_node = self.build_node(node)

    self.cfg.attach_child(cfg_node)
    self.cfg.go_to(cfg_node.name)

    for child in iter_child_nodes(node):
      self.visit(child)


  def generic_visit(self, node: AST) -> Any:
    self.cfg.get_cur().append_contents(node)
    return super().generic_visit(node)


  def build_node(self, node: AST) -> Node:
    return Node(
      name=f"{node.__class__.__name__}_{node.lineno}_{node.col_offset}",
      start=Location(node.lineno, node.col_offset),
      end=Location(node.end_lineno, node.end_col_offset),
      contents=[node]
    )