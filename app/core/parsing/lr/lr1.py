from collections import deque

from app.core.parsing.lr.lr_base import LRBase

from app.core.automata.state import State
from app.core.automata.transition import Transition

from app.core.parsing.lr.items.lr1_item import LR1Item

from app.core.grammar.first_follow import (
    compute_first,
    first_of_sequence
)

from app.utils.constants import (
    EPSILON,
    ENDMARKER
)


class LR1(LRBase):

    def __init__(self, grammar):

        #
        # FIRST
        #

        self.first_sets = {}

        #
        # item -> NFA state
        #

        self.item_to_nfa_state = {}

        #
        # DFA canonical collection map
        #

        self.dfa_state_map = {}

        super().__init__(grammar)

    #
    # ==========================================================
    # LR1 VALIDATION
    # ==========================================================
    #

    @property
    def is_valid(self):

        return len(self.conflicts) == 0

    #
    # ==========================================================
    # FIRST
    # ==========================================================
    #

    def build_first_sets(self):

        self.first_sets = compute_first(
            self.grammar
        )

    #
    # ==========================================================
    # NFA
    # ==========================================================
    #

    def build_nfa(self):
        self.build_first_sets()
        state_id = 0
        augmented_production = self.grammar.productions[0]
        initial_item = LR1Item(
            production=augmented_production,
            dot_position=0,
            lookahead=ENDMARKER
        )

        queue = deque([
            initial_item
        ])

        visited = set()

        #
        # helper
        #

        def get_or_create_state(item):

            nonlocal state_id

            if item in self.item_to_nfa_state:
                return self.item_to_nfa_state[item]

            state = State(
                id=state_id
            )

            state.add_item(item)

            self.nfa.add_state(state)

            self.item_to_nfa_state[item] = state

            state_id += 1

            return state

        #
        # initial state
        #

        initial_state = get_or_create_state(
            initial_item
        )

        self.nfa.initial_state = initial_state

        #
        # BFS
        #

        while queue:

            item = queue.popleft()

            if item in visited:
                continue

            visited.add(item)

            source_state = self.item_to_nfa_state[
                item
            ]

            #
            # complete item
            #

            if item.is_complete():
                continue

            next_symbol = item.next_symbol()

            #
            # ======================================================
            # NORMAL TRANSITION
            # ======================================================
            #

            advanced_item = item.advance()

            target_state = get_or_create_state(
                advanced_item
            )

            transition = Transition(
                source_id=source_state.id,
                symbol=next_symbol,
                target_id=target_state.id
            )

            self.nfa.add_transition(
                transition
            )

            if advanced_item not in visited:
                queue.append(
                    advanced_item
                )

            #
            # ======================================================
            # EPSILON TRANSITIONS
            # ======================================================
            #

            if next_symbol not in self.grammar.non_terminals:
                continue

            lookaheads = first_of_sequence(
                item.next_sequence(),
                self.first_sets
            )

            lookaheads.discard(
                EPSILON
            )

            productions = self.grammar.get_productions_for(
                next_symbol
            )

            for production in productions:

                for lookahead in lookaheads:

                    target_item = LR1Item(
                        production=production,
                        dot_position=0,
                        lookahead=lookahead
                    )

                    target_state = get_or_create_state(
                        target_item
                    )

                    epsilon_transition = Transition(
                        source_id=source_state.id,
                        symbol=EPSILON,
                        target_id=target_state.id
                    )

                    self.nfa.add_transition(
                        epsilon_transition
                    )

                    if target_item not in visited:
                        queue.append(
                            target_item
                        )

   
    #
    # ==========================================================
    # EPSILON CLOSURE
    # ==========================================================
    #

    def epsilon_closure(self, states):

        closure = set(states)

        stack = list(states)

        while stack:

            state = stack.pop()

            transitions = self.nfa.get_transitions_by_symbol(
                state,
                EPSILON
            )

            for transition in transitions:

                target_state = self.nfa.get_state(
                    transition.target_id
                )

                if target_state not in closure:

                    closure.add(target_state)

                    stack.append(target_state)

        return closure

    #
    # ==========================================================
    # MOVE
    # ==========================================================
    #

    def move(self, states, symbol):

        result = set()

        for state in states:

            transitions = self.nfa.get_transitions_by_symbol(
                state,
                symbol
            )

            for transition in transitions:

                target_state = self.nfa.get_state(
                    transition.target_id
                )

                result.add(target_state)

        return result

    #
    # ==========================================================
    # DFA
    # ==========================================================
    #

    def build_dfa(self):

        dfa_state_id = 0

        #
        # initial closure
        #

        initial_closure = self.epsilon_closure(
            {self.nfa.initial_state}
        )

        initial_closure_frozen = frozenset(
            initial_closure
        )

        initial_dfa_state = State(
            id=dfa_state_id
        )

        #
        # copy LR1 items
        #

        for nfa_state in initial_closure:

            for item in nfa_state.items:
                initial_dfa_state.add_item(item)

        self.dfa.add_state(
            initial_dfa_state
        )

        self.dfa.initial_state = (
            initial_dfa_state
        )

        #
        # map:
        # frozenset(NFA states) -> DFA state
        #

        self.dfa_state_map[
            initial_closure_frozen
        ] = initial_dfa_state

        queue = deque([
            initial_closure_frozen
        ])

        dfa_state_id += 1

        #
        # subset construction
        #

        while queue:

            current_closure = queue.popleft()

            current_dfa_state = self.dfa_state_map[
                current_closure
            ]

            symbols = set()

            #
            # collect symbols
            #

            for nfa_state in current_closure:

                for item in nfa_state.items:

                    next_symbol = item.next_symbol()

                    if next_symbol is not None:
                        symbols.add(next_symbol)

            #
            # transitions
            #

            for symbol in symbols:

                moved = self.move(
                    current_closure,
                    symbol
                )

                if not moved:
                    continue

                target_closure = self.epsilon_closure(
                    moved
                )

                target_closure_frozen = frozenset(
                    target_closure
                )

                #
                # new DFA state
                #

                if (
                    target_closure_frozen
                    not in self.dfa_state_map
                ):

                    new_state = State(
                        id=dfa_state_id
                    )

                    for nfa_state in target_closure:

                        for item in nfa_state.items:
                            new_state.add_item(item)

                    self.dfa.add_state(
                        new_state
                    )

                    self.dfa_state_map[
                        target_closure_frozen
                    ] = new_state

                    queue.append(
                        target_closure_frozen
                    )

                    dfa_state_id += 1

                target_dfa_state = self.dfa_state_map[
                    target_closure_frozen
                ]

                transition = Transition(
                    source_id=current_dfa_state.id,
                    symbol=symbol,
                    target_id=target_dfa_state.id
                )

                self.dfa.add_transition(
                    transition
                )

    #
    # ==========================================================
    # SHIFT ACTIONS
    # ==========================================================
    #

    def build_shift_actions(self):

        for state in self.dfa.states.values():

            for item in state.items:

                if item.is_complete():
                    continue

                symbol = item.next_symbol()

                #
                # only terminals
                #

                if symbol not in self.grammar.terminals:
                    continue

                transitions = self.dfa.get_transitions_by_symbol(
                    state,
                    symbol
                )

                if not transitions:
                    continue

                target = transitions[0].target_id

                self.add_action(
                    state.id,
                    symbol,
                    f"s{target}"
                )

    #
    # ==========================================================
    # REDUCE ACTIONS
    # ==========================================================
    #

    def build_reduce_actions(self):

        for state in self.dfa.states.values():

            for item in state.items:

                #
                # only completed items
                #

                if not item.is_complete():
                    continue

                production = item.production

                #
                # accept
                #
                # [S' -> S., $]
                #

                if (
                    production.left
                    == self.grammar.augmented_start_symbol
                    and item.lookahead == ENDMARKER
                ):

                    self.add_action(
                        state.id,
                        ENDMARKER,
                        "accept"
                    )

                    continue

                #
                # LR1 reduction only on item lookahead
                #

                self.add_action(
                    state.id,
                    item.lookahead,
                    f"r{production.id}"
                )

    #
    # ==========================================================
    # GOTO TABLE
    # ==========================================================
    #

    def build_goto_entries(self):

        for state in self.dfa.states.values():

            for non_terminal in self.grammar.non_terminals:

                if (
                    non_terminal
                    == self.grammar.augmented_start_symbol
                ):
                    continue

                transitions = self.dfa.get_transitions_by_symbol(
                    state,
                    non_terminal
                )

                if not transitions:
                    continue

                target = transitions[0].target_id

                self.add_goto(
                    state.id,
                    non_terminal,
                    target
                )

    #
    # ==========================================================
    # PARSING TABLE
    # ==========================================================
    #

    def build_parsing_table(self):

        self.build_shift_actions()

        self.build_reduce_actions()

        self.build_goto_entries()