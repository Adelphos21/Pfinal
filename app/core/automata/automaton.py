from dataclasses import dataclass, field
from app.core.automata.state import State
from app.core.automata.transition import Transition


@dataclass
class Automaton:

    states: dict[int, State] = field(
        default_factory=dict
    )

    transitions: set[Transition] = field(
        default_factory=set
    )

    initial_state: State | None = None

    def add_state(self,state: State):
        self.states[state.id] = state

    def add_transition(self, transition: Transition):
        self.transitions.add(transition)

    def get_state( self, state_id: int):
        return self.states.get(state_id)

    def get_transitions_from( self, state: State):
        return [
            transition
            for transition in self.transitions
            if transition.source_id == state.id
        ]

    def get_transitions_by_symbol(self,state: State, symbol: str):
        return [
            transition
            for transition in self.transitions
            if (
                transition.source_id == state.id
                and transition.symbol == symbol
            )
        ]

    def __str__(self):

        lines = []
        lines.append("States:")

        for state in sorted( self.states.values(), key=lambda s: s.id ):
            lines.append(str(state))

        lines.append("")
        lines.append("Transitions:")

        for transition in sorted( self.transitions, key=lambda t: ( t.source_id, t.target_id)):
            lines.append(
                str(transition)
            )

        return "\n".join(lines)