from dataclasses import dataclass, field

from app.core.tracing.trace_frame import (
    TraceFrame
)


@dataclass
class TraceRecorder:

    frames: list[TraceFrame] = field(
        default_factory=list
    )

    #
    # ==================================================
    # RECORD FRAME
    # ==================================================
    #

    def record(
        self,
        parsing_stack,
        semantic_stack,
        remaining_input,
        action
    ):

        frame = TraceFrame(
            parsing_stack=list(parsing_stack),
            semantic_stack=list(semantic_stack),
            remaining_input=list(remaining_input),
            action=action
        )

        self.frames.append(frame)

    #
    # ==================================================
    # EXPORT
    # ==================================================
    #

    def to_dict(self):

        return {
            "frames": [
                frame.to_dict()
                for frame in self.frames
            ]
        }