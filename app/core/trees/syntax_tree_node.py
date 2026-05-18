from dataclasses import dataclass, field


@dataclass
class SyntaxTreeNode:

    symbol: str

    children: list = field(
        default_factory=list
    )

    def add_child(self, child):

        self.children.append(child)

    def is_leaf(self):

        return len(self.children) == 0

    def pretty(
        self,
        level=0
    ):

        indent = "  " * level

        lines = [
            f"{indent}{self.symbol}"
        ]

        for child in self.children:

            lines.append(
                child.pretty(level + 1)
            )

        return "\n".join(lines)

    def __str__(self):

        return self.pretty()