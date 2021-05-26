from cfg import CFG
from node import Node, Location, Event
from typing import Any, List, Set
import ast


class CFGBuilder(ast.NodeVisitor):
  cfg: CFG
  cur_event: Event
  returning: bool
  visited_nodes: Set[str]


  def __init__(self):
    super().__init__()

  def build(self, node: ast.AST) -> CFG:
    self.cfg = CFG('test', 'root', 'root', {'root': Node('root')})
    self.cur_event = Event.CONTINUE
    self.returning = False
    self.visited_nodes = {}
    self._visit_block(node.body)
    return self.cfg


  def _visit_block(self, nodes: List[ast.stmt | ast.expr]) -> None:
    for node in nodes:
      self.visit(node)


  def generic_visit(self, node: ast.AST) -> Any:
    print(ast.dump(node))
    if self.cur_event != Event.CONTINUE:
      cfg_node = self._build_node(node)
      self.cfg.attach_child(cfg_node, self.cur_event)
      self.cfg.go_to(cfg_node.name)
      self.cur_event = Event.CONTINUE
    else:
      self.cfg.get_cur().append_contents(node)


  def visit_While(self, node: ast.For) -> Any:
    cfg_node = self._build_node(node)
    self.cfg.attach_child(cfg_node, self.cur_event)

    if node.body:
      self.cur_event = Event.ONTRUE


  def visit_If(self, node: ast.If) -> Any:
    cfg_node = self._build_node(node)
    exit_node = self._build_empty_node(f"exit_{cfg_node.name}", Location.default_end(node))
    self.cfg.attach_child(cfg_node, self.cur_event)
    self.cfg.go_to(cfg_node.name)

    if node.body:
      self.cur_event = Event.ONTRUE
      self._visit_block(node.body)
      self._add_exit(exit_node)
      self.cfg.go_to(cfg_node.name)

    if node.orelse:
      self.cur_event = Event.ONFALSE
      self._visit_block(node.orelse)

    self._add_exit(exit_node)
    self.cfg.go_to(exit_node.name)


  def visit_Return(self, node: ast.Return) -> Any:
    self.cfg.attach_child(self._build_node(node))
    self.returning = True


  def _visit_body(self, body: List[ast.stmt | ast.expr], event: Event = Event.CONTINUE):
    children = iter(body)
    body_node = self._build_node(children.__next__())
    self.cfg.attach_child(body_node, event)
    self.cfg.go_to(body_node.name)

    for child in children:
      self.visit(child)


  def _add_exit(self, exit_node: Node):
    if self.returning:
      self.returning = False
    else:
      self.cfg.attach_child(exit_node)


  def _build_node(self, node: ast.AST, name: str = '') -> Node:
    return Node(
      name=name or f"{node.__class__.__name__}_{node.lineno}_{node.col_offset}",
      start=Location.default_start(node),
      end=Location.default_end(node),
      contents=[node]
    )


  def _build_empty_node(self,  name: str, location: Location) -> Node:
    return Node(name=name, start=location, end=location)