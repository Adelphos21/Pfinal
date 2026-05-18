from dataclasses import dataclass, field


@dataclass
class TraceFrame:

    parsing_stack: list = field(
        default_factory=list
    )

    semantic_stack: list = field(
        default_factory=list
    )

    remaining_input: list = field(
        default_factory=list
    )

    action: str = ""

    def to_dict(self):

        return {
            "parsing_stack": self.parsing_stack,
            "semantic_stack": self.semantic_stack,
            "remaining_input": self.remaining_input,
            "action": self.action
        }

    def __str__(self):

        return (
            f"STACK     : {self.parsing_stack}\n"
            f"SEMANTIC  : {self.semantic_stack}\n"
            f"INPUT     : {self.remaining_input}\n"
            f"ACTION    : {self.action}"
        )