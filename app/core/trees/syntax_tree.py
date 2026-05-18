from dataclasses import dataclass

from app.core.trees.syntax_tree_node import (
    SyntaxTreeNode
)

@dataclass
class SyntaxTree:

    root: SyntaxTreeNode

    def __str__(self):

        return str(self.root)