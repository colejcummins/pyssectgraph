from .cfg import CFG
import ast


class CFGBuilder(ast.NodeVisitor):
  cfg: CFG

  def visit_If(self, node: ast.AST):
    node.test

