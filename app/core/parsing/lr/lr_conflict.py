from dataclasses import dataclass


@dataclass
class LRConflict:

    state: int

    symbol: str

    old_action: str

    new_action: str

    conflict_type: str

    def __str__(self):

        return (
            f"{self.conflict_type} conflict "
            f"in state {self.state} "
            f"with symbol '{self.symbol}': "
            f"{self.old_action} / {self.new_action}"
        )