from app.core.parsing.lr.lr0 import LR0

from app.core.grammar.first_follow import (
    compute_first,
    compute_follow
)

from app.utils.constants import ENDMARKER


class SLR1(LR0):

    def __init__(self, grammar):

        #
        # FIRST/FOLLOW
        #

        self.first_sets = {}
        self.follow_sets = {}

        super().__init__(grammar)

    #
    # ==========================================================
    # SLR1 VALIDATION
    # ==========================================================
    #

    @property
    def is_valid(self):

        return len(self.conflicts) == 0

    #
    # ==========================================================
    # FIRST/FOLLOW
    # ==========================================================
    #

    def build_first_follow_sets(self):

        self.first_sets = compute_first(
            self.grammar
        )

        self.follow_sets = compute_follow(
            self.grammar,
            self.first_sets
        )

    #
    # ==========================================================
    # SHIFT ACTIONS
    # ==========================================================
    #

    def build_shift_actions(self):

        for state in self.dfa.states.values():

            for item in state.items:

                #
                # complete item
                #

                if item.is_complete():
                    continue

                symbol = item.next_symbol()

                #
                # only terminals produce shifts
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
                # only complete items
                #

                if not item.is_complete():
                    continue

                production = item.production

                #
                # augmented production
                #
                # S' -> S
                #

                if (
                    production.left
                    == self.grammar.augmented_start_symbol
                ):

                    self.add_action(
                        state.id,
                        ENDMARKER,
                        "accept"
                    )

                    continue

                #
                # reduce on FOLLOW(A)
                #

                follow = self.follow_sets[
                    production.left
                ]

                for terminal in follow:

                    self.add_action(
                        state.id,
                        terminal,
                        f"r{production.id}"
                    )

    #
    # ==========================================================
    # PARSING TABLE
    # ==========================================================
    #

    def build_parsing_table(self):

        #
        # FIRST/FOLLOW
        #

        self.build_first_follow_sets()

        #
        # tables
        #

        self.build_shift_actions()

        self.build_reduce_actions()

        self.build_goto_entries()