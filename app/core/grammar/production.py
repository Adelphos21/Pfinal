from dataclasses import dataclass

@dataclass(frozen=True)
class Production:

    id: int

    left: str

    right: tuple[str, ...]

    def __str__(self):
        return (
            f"[{self.id}] "
            f"{self.left} -> "
            f"{' '.join(self.right)}"
        )