from dataclasses import dataclass

from app.core.parsing.lr.items.lr0_item import LR0Item


@dataclass(frozen=True)
class LR1Item(LR0Item):

    lookahead: str = "$"

    def beta(self):

        return self.production.right[
            self.dot_position + 1:
        ]

    def next_sequence(self):

        return (
            self.beta()
            + (self.lookahead,)
        )

    def advance(self):

        if self.is_complete():

            raise ValueError(
                "Cannot advance completed item"
            )

        return LR1Item(
            production=self.production,
            dot_position=self.dot_position + 1,
            lookahead=self.lookahead
        )
    
    def __hash__(self):

        return hash((
            self.production.id,
            self.dot_position,
            self.lookahead
        ))
    

    def __eq__(self, other):

        return (
            isinstance(other, LR1Item)
            and self.production.id == other.production.id
            and self.dot_position == other.dot_position
            and self.lookahead == other.lookahead
        )

    def __str__(self):

        right = list(self.production.right)

        right.insert(
            self.dot_position,
            "•"
        )

        return (
            f"[{self.production.left} -> "
            f"{' '.join(right)}, "
            f"{self.lookahead}]"
        )