from dataclasses import dataclass


@dataclass(frozen=True)
class Transition:

    source_id: int

    symbol: str

    target_id: int

    def __str__(self):

        return (
            f"I{self.source_id} "
            f"--{self.symbol}--> "
            f"I{self.target_id}"
        )