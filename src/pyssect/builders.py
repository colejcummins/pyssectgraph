from dataclasses import dataclass
from types import CodeType, FrameType, FunctionType
from .graph import PyssectGraph
from .node import PyssectNode, Location, ControlEvent
from typing import Any, Iterator, List, Dict, Union
from inspect import getsource
import dis
import ast


class ASTtoCFG(ast.NodeVisitor):
  """Class that extends the ast Node Visitor class, builds a PyssectGraph from an ast"""
  cfg_dict: Dict[str,PyssectGraph]
  cfg: PyssectGraph
  cur_event: ControlEvent
  interrupting: bool
  headers: List[PyssectNode]
  exits: List[PyssectNode]


  def __init__(self):
    self._init_instances()
    super().__init__()


  def build(self, node: ast.AST, do_clean: bool = False) -> Dict[str, PyssectGraph]:
    self._init_instances()
    cfg = PyssectGraph('__main__', nodes={'root': PyssectNode('root')})
    self.cfg_dict['__main__'] = cfg
    self.cfg = cfg
    if hasattr(node, 'body'):
      self._visit_block(node.body)
    else:
      self.visit(node)

    if do_clean:
      self.clean_graphs()

    return self.cfg_dict


  def clean_graphs(self):
    for cfg in self.cfg_dict.values():
      cfg.clean_graph()


  def _init_instances(self):
    self.cur_event = ControlEvent.PASS
    self.cfg_dict = {}
    self.interrupting = False
    self.headers = []
    self.exits = []


  def _visit_block(self, nodes: List[Union[ast.stm, ast.expr]]) -> None:
    for node in nodes:
      if self.interrupting:
        break
      self.visit(node)


  def generic_visit(self, node: ast.AST) -> Any:
    if self.cur_event != ControlEvent.PASS:
      cfg_node = self._build_node(node)
      self.cfg.attach_child(cfg_node, self.cur_event)
      self.cfg.go_to(cfg_node.name)
      self.cur_event = ControlEvent.PASS
    else:
      self.cfg.get_cur().append_contents(node)


  def visit_ClassDef(self, node: ast.ClassDef) -> Any:
    self._visit_block(node.body)


  def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
    saved = self.cfg.name
    cfg_node = self._build_node(node)
    self.cfg.attach_child(cfg_node, self.cur_event)
    self.cfg.go_to(cfg_node.name)

    new_cfg = PyssectGraph(node.name, nodes={'root': PyssectNode()})
    self.cfg_dict[node.name] = new_cfg
    self.cfg = new_cfg
    self._visit_block(node.body)

    self.cfg = self.cfg_dict[saved]
    self.interrupting = False


  def visit_Import(self, node: ast.Import) -> Any:
    pass


  def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
    pass


  def visit_While(self, node: ast.While) -> Any:
    self._visit_loop(node)


  def visit_For(self, node: ast.For) -> Any:
    self._visit_loop(node)


  def _visit_loop(self, node: Union[ast.For, ast.While]) -> Any:
    cfg_node = self._build_node(node)
    exit_node = self._build_empty_node(f"exit_{cfg_node.name}", Location.default_end(node))
    self.headers.append(cfg_node)
    self.exits.append(exit_node)
    self.cfg.attach_child(cfg_node, self.cur_event)
    self.cfg.go_to(cfg_node.name)

    if node.body:
      self._visit_body(node, cfg_node, cfg_node.name)

    if node.orelse:
      self.cur_event = ControlEvent.ONFALSE
      self._visit_block(node.orelse)

    self._add_exit(exit_node)
    self.cfg.go_to(exit_node.name)

    self.headers.pop()
    self.exits.pop()
    self.cur_event = ControlEvent.PASS


  def visit_If(self, node: ast.If) -> Any:
    cfg_node = self._build_node(node)
    exit_node = self._build_empty_node(f"exit_{cfg_node.name}", Location.default_end(node))
    self.cfg.attach_child(cfg_node, self.cur_event)
    self.cfg.go_to(cfg_node.name)

    if node.body:
      self._visit_body(node, exit_node, cfg_node.name)

    if node.orelse:
      self.cur_event = ControlEvent.ONFALSE
      self._visit_block(node.orelse)

    self._add_exit(exit_node)
    self.cfg.go_to(exit_node.name)
    self.cur_event = ControlEvent.PASS


  def visit_Try(self, node: ast.Try) -> Any:
    cfg_node = self._build_node(node)
    try_block = None
    exit_parents: List[PyssectNode] = []
    exit_node = self._build_empty_node(f"exit_{cfg_node.name}", Location.default_end(node))
    self.cfg.attach_child(cfg_node, self.cur_event)
    self.cfg.go_to(cfg_node.name)

    if node.body:
      self.cur_event = ControlEvent.ONTRY
      self._visit_block(node.body)
      try_block = self.cfg.nodes[self.cfg.cur]

    for handler in node.handlers:
      self.visit(handler)
      exit_parents.append(self.cfg.nodes[self.cfg.cur])
      self.cfg.go_to(try_block.name if try_block else cfg_node.name)

    if node.orelse:
      self.cur_event = ControlEvent.ONFALSE
      self._visit_block(node.orelse)
      exit_parents.append(self.cfg.nodes[self.cfg.cur])

    if node.finalbody:
      self.cur_event = ControlEvent.ONFINALLY
      self._visit_block(node.finalbody)
      for exit in exit_parents:
        self.cfg.attach_parent(exit, ControlEvent.ONFINALLY)

    self.cfg.attach_child(exit_node)
    self.cfg.go_to(exit_node.name)


  def visit_ExceptHandler(self, node: ast.ExceptHandler) -> Any:
    cfg_node = self._build_node(node)
    self.cfg.attach_child(cfg_node, ControlEvent.ONEXCEPTION)
    self._visit_block(node.body)
    self.cfg.go_to(cfg_node.name)


  def visit_Return(self, node: ast.Return) -> Any:
    self._visit_interrupts(node)


  def visit_Yield(self, node: ast.Yield) -> Any:
    self._visit_interrupts(node)


  def visit_YieldFrom(self, node: ast.YieldFrom) -> Any:
    # TODO implement yieldfrom
    self._visit_interrupts(node)


  def _visit_interrupts(self, node: ast.AST) -> Any:
    self.cfg.attach_child(self._build_node(node))
    self.interrupting = True


  def visit_Break(self, node: ast.Break) -> Any:
    cfg_node = self._build_node(node)
    self.cfg.attach_child(cfg_node)
    self.cfg.go_to(cfg_node.name)
    self.cfg.attach_child(self.exits[-1], ControlEvent.ONBREAK)
    self.interrupting = True


  def visit_Continue(self, node: ast.Continue) -> Any:
    cfg_node = self._build_node(node)
    self.cfg.attach_child(cfg_node)
    self.cfg.go_to(cfg_node.name)
    self.cfg.attach_child(self.headers[-1], ControlEvent.ONCONTINUE)
    self.interrupting = True


  def _visit_body(self, node: ast.AST, exit: PyssectNode, parent_name: str):
    self.cur_event = ControlEvent.ONTRUE
    self._visit_block(node.body)
    self._add_exit(exit)
    self.cfg.go_to(parent_name)


  def _add_exit(self, exit_node: PyssectNode):
    if self.interrupting:
      self.interrupting = False
    else:
      self.cfg.attach_child(exit_node)


  def _build_node(self, node: ast.AST, name: str = '') -> PyssectNode:
    return PyssectNode(
      name=name or f"{node.__class__.__name__}_{node.lineno}_{node.col_offset}",
      start=Location.default_start(node),
      end=Location.default_end(node),
      contents=[node]
    )


  def _build_empty_node(self,  name: str, location: Location) -> PyssectNode:
    return PyssectNode(name=name, start=location, end=location)


@dataclass
class CodetoCFG():
  cfg: PyssectGraph

  def build(self, code: CodeType) -> PyssectGraph:
    self.cfg = PyssectGraph('test', 'root', 'root', {'root': PyssectNode('root')})
    self._visit_code(dis.get_instructions(code))
    return self.cfg

  def _visit_block(self, block: Iterator[dis.Instruction]):
    for instruction in block:
      self.visit(instruction)


  def generic_visit(self, inst: dis.Instruction):
    self.cfg.get_cur().append_contents(inst)


  def visit(self, inst: dis.Instruction):
    getattr(self, f'visit_{inst.opname.lower()}', self.generic_visit)(inst)


def builds(source: Union[str, CodeType, FrameType, FunctionType], do_clean: bool = False) -> Dict[str, PyssectGraph]:
  """Takes a python source object and returns the corresponding PyssectGraph"""
  return ASTtoCFG().build(ast.parse(source if isinstance(source, str) else getsource(source)), do_clean)


def builds_file(file: str, do_clean: bool = False) -> Dict[str, PyssectGraph]:
  """Takes a python file and returns the corresponding PyssectGraph"""
  with open(file, 'r') as f:
    return ASTtoCFG().build(ast.parse(f.read()), do_clean)