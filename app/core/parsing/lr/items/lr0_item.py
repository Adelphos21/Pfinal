from dataclasses import dataclass

from app.core.grammar.production import Production


@dataclass(frozen=True)
class LR0Item:

    production: Production

    dot_position: int = 0

    def next_symbol(self) -> str | None:

        if self.dot_position >= len(self.production.right):
            return None

        return self.production.right[
            self.dot_position
        ]

    def is_complete(self) -> bool:

        return (
            self.dot_position
            >= len(self.production.right)
        )

    def advance(self):

        if self.is_complete():

            raise ValueError(
                "Cannot advance completed item"
            )

        return LR0Item(
            production=self.production,
            dot_position=self.dot_position + 1
        )

    def __str__(self):

        right = list(self.production.right)

        right.insert(
            self.dot_position,
            "•"
        )

        return (
            f"{self.production.left} -> "
            f"{' '.join(right)}"
        )