from collections import deque

from app.core.parsing.lr.lr_base import LRBase

from app.core.automata.state import State
from app.core.automata.transition import Transition

from app.core.parsing.lr.items.lr0_item import LR0Item

from app.utils.constants import ENDMARKER, EPSILON


class LR0(LRBase):

    def __init__(self, grammar):

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
    # LR0 VALIDATION
    # ==========================================================
    #

    @property
    def is_valid(self):

        return len(self.conflicts) == 0

    def validate_lr0_states(self):

        for state in self.dfa.states.values():

            complete_items = []
            shift_items = []

            for item in state.items:

                #
                # complete item
                #

                if item.is_complete():

                    complete_items.append(item)

                    continue

                #
                # shift item
                #

                next_symbol = item.next_symbol()

                if next_symbol in self.grammar.terminals:

                    shift_items.append(item)

            #
            # reduce/reduce conflict
            #

            if len(complete_items) > 1:

                for i in range(len(complete_items)):

                    for j in range(i + 1, len(complete_items)):

                        left = complete_items[i]
                        right = complete_items[j]

                        self.register_conflict(
                            state=state.id,
                            symbol=None,
                            old_action=f"r{left.production.id}",
                            new_action=f"r{right.production.id}"
                        )

            #
            # shift/reduce conflict
            #

            if complete_items and shift_items:

                for reduce_item in complete_items:

                    for shift_item in shift_items:

                        symbol = shift_item.next_symbol()

                        transitions = self.dfa.get_transitions_by_symbol(state, symbol)

                        if not transitions:
                            continue

                        target = transitions[0].target_id

                        self.register_conflict(
                            state=state.id,
                            symbol=symbol,
                            old_action=f"r{reduce_item.production.id}",
                            new_action=f"s{target}"
                        )

    #
    # ==========================================================
    # NFA
    # ==========================================================
    #

    def build_nfa(self):

        state_id = 0

        #
        # create NFA states
        #

        for production in self.grammar.productions:

            for dot_position in range(len(production.right) + 1):

                item = LR0Item(
                    production=production,
                    dot_position=dot_position
                )

                state = State(id=state_id)

                state.add_item(item)

                self.nfa.add_state(state)

                self.item_to_nfa_state[item] = state

                #
                # initial state
                #

                if (
                    production.left == self.grammar.augmented_start_symbol
                    and dot_position == 0
                ):

                    self.nfa.initial_state = state

                state_id += 1

        #
        # create transitions
        #

        for item, source_state in self.item_to_nfa_state.items():

            #
            # completed item
            #

            if item.is_complete():
                continue

            next_symbol = item.next_symbol()

            advanced_item = item.advance()

            target_state = self.item_to_nfa_state[advanced_item]

            #
            # normal transition
            #

            transition = Transition(
                source_id=source_state.id,
                symbol=next_symbol,
                target_id=target_state.id
            )

            self.nfa.add_transition(transition)

            #
            # epsilon transitions
            #

            if next_symbol in self.grammar.non_terminals:

                productions = self.grammar.get_productions_for(next_symbol)

                for production in productions:

                    target_item = LR0Item(
                        production=production,
                        dot_position=0
                    )

                    epsilon_target = self.item_to_nfa_state[target_item]

                    epsilon_transition = Transition(
                        source_id=source_state.id,
                        symbol=EPSILON,
                        target_id=epsilon_target.id
                    )

                    self.nfa.add_transition(epsilon_transition)

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

            transitions = self.nfa.get_transitions_by_symbol(state, EPSILON)

            for transition in transitions:

                target_state = self.nfa.get_state(transition.target_id)

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

            transitions = self.nfa.get_transitions_by_symbol(state, symbol)

            for transition in transitions:

                target_state = self.nfa.get_state(transition.target_id)

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

        initial_closure = self.epsilon_closure({self.nfa.initial_state})

        initial_items = frozenset(
            state.item
            for state in initial_closure
        )

        initial_dfa_state = State(id=dfa_state_id)

        for item in initial_items:
            initial_dfa_state.add_item(item)

        self.dfa.add_state(initial_dfa_state)

        self.dfa.initial_state = initial_dfa_state

        self.dfa_state_map[initial_items] = initial_dfa_state

        queue = deque([initial_items])

        dfa_state_id += 1

        #
        # subset construction
        #

        while queue:

            current_items = queue.popleft()

            current_dfa_state = self.dfa_state_map[current_items]

            #
            # possible symbols
            #

            symbols = set()

            for item in current_items:

                next_symbol = item.next_symbol()

                if next_symbol is not None:
                    symbols.add(next_symbol)

            #
            # transitions
            #

            for symbol in symbols:

                nfa_states = set()

                for item in current_items:

                    source_state = self.item_to_nfa_state[item]

                    nfa_states.add(source_state)

                moved = self.move(nfa_states, symbol)

                closure = self.epsilon_closure(moved)

                target_items = frozenset(
                    state.item
                    for state in closure
                )

                if not target_items:
                    continue

                #
                # create new DFA state
                #

                if target_items not in self.dfa_state_map:

                    new_state = State(id=dfa_state_id)

                    for item in target_items:
                        new_state.add_item(item)

                    self.dfa.add_state(new_state)

                    self.dfa_state_map[target_items] = new_state

                    queue.append(target_items)

                    dfa_state_id += 1

                target_dfa_state = self.dfa_state_map[target_items]

                transition = Transition(
                    source_id=current_dfa_state.id,
                    symbol=symbol,
                    target_id=target_dfa_state.id
                )

                self.dfa.add_transition(transition)

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
                # only terminals produce shift
                #

                if symbol not in self.grammar.terminals:
                    continue

                transitions = self.dfa.get_transitions_by_symbol(state, symbol)

                if not transitions:
                    continue

                target = transitions[0].target_id

                self.add_action(
                    state.id,
                    symbol,
                    f"s{target}",
                    register_conflict=False
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
                # solo completos
                #

                if not item.is_complete():
                    continue

                production = item.production

                #
                # ACCEPT
                #

                if (
                    production.left
                    == self.grammar.augmented_start_symbol
                ):

                    self.add_action(
                        state.id,
                        ENDMARKER,
                        "accept",
                        register_conflict=False
                    )

                    continue

                #
                # LR(0):
                # reduce en TODOS
                # los terminales + $
                #

                all_terminals = (
                    set(self.grammar.terminals)
                    | {ENDMARKER}
                )

                for terminal in all_terminals:

                    self.add_action(
                        state.id,
                        terminal,
                        f"r{production.id}",
                        register_conflict=False
                    )
    #
    # ==========================================================
    # GOTO TABLE
    # ==========================================================
    #

    def build_goto_entries(self):

        for state in self.dfa.states.values():

            for non_terminal in self.grammar.non_terminals:

                #
                # augmented symbol never appears in GOTO table
                #

                if non_terminal == self.grammar.augmented_start_symbol:
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

        #
        # formal LR0 validation
        #

        self.validate_lr0_states()