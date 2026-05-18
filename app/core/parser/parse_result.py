from dataclasses import dataclass

from app.core.trees.syntax_tree import (
    SyntaxTree
)

from app.core.tracing.trace_recorder import (
    TraceRecorder
)


@dataclass
class ParseResult:

    accepted: bool

    trace: TraceRecorder | None = None

    error: str | None = None

    syntax_tree: SyntaxTree | None = None