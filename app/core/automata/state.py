from dataclasses import dataclass, field


@dataclass
class State:

    id: int

    items: set = field(default_factory=set)

    is_accepting: bool = False

    def add_item(self, item):

        self.items.add(item)

    def __contains__(self, item):

        return item in self.items

    def __iter__(self):

        return iter(self.items)

    def __len__(self):

        return len(self.items)
    
    @property
    def item(self):
        return next(iter(self.items))

    
    def __hash__(self):

        return hash(self.id)

    def __eq__(self, other):

        return (
            isinstance(other, State)
            and self.id == other.id
        )

    def __str__(self):

        lines = [
            f"I{self.id}:"
        ]

        for item in sorted(
            self.items,
            key=str
        ):
            lines.append(
                f"  {item}"
            )

        return "\n".join(lines)