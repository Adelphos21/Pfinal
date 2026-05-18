from collections import defaultdict

from app.core.grammar.first_follow import (
    compute_first,
    compute_follow,
    first_of_sequence
)

from app.core.parser.abstract_parser import (
    AbstractParser
)

from app.core.parser.predictive_runtime import (
    PredictiveRuntime
)

from app.utils.constants import (
    EPSILON
)


class LL1(AbstractParser):

    def __init__(self, grammar):

        self.grammar = grammar

        #
        # FIRST/FOLLOW
        #

        self.first_sets = {}

        self.follow_sets = {}

        #
        # parsing table
        #
        # M[A, a] = set(productions)
        #

        self.parsing_table = defaultdict(set)

        #
        # conflicts
        #

        self.conflicts = []

        #
        # build
        #

        self.build()

    #
    # ==========================================================
    # BUILD
    # ==========================================================
    #

    def build(self):

        self.build_first_follow_sets()

        self.build_parsing_table()

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
    # TABLE HELPERS
    # ==========================================================
    #

    def add_table_entry(
        self,
        non_terminal,
        terminal,
        production
    ):

        key = (
            non_terminal,
            terminal
        )

        old_productions = self.parsing_table[key]

        #
        # same production
        #

        if production in old_productions:
            return

        #
        # conflicts
        #

        for old_production in old_productions:

            self.conflicts.append({
                "non_terminal": non_terminal,
                "terminal": terminal,
                "old": old_production,
                "new": production
            })

        #
        # store
        #

        self.parsing_table[key].add(
            production
        )

    #
    # ==========================================================
    # BUILD PARSING TABLE
    # ==========================================================
    #

    def build_parsing_table(self):

        for production in self.grammar.productions:

            left = production.left

            right = production.right

            #
            # FIRST(alpha)
            #

            first_alpha = first_of_sequence(
                right,
                self.first_sets
            )

            #
            # RULE 1
            #

            for terminal in (
                first_alpha - {EPSILON}
            ):

                self.add_table_entry(
                    left,
                    terminal,
                    production
                )

            #
            # RULE 2
            #

            if EPSILON in first_alpha:

                for terminal in self.follow_sets[left]:

                    self.add_table_entry(
                        left,
                        terminal,
                        production
                    )

    #
    # ==========================================================
    # VALIDATION
    # ==========================================================
    #

    @property
    def is_valid(self):

        return len(self.conflicts) == 0

    #
    # ==========================================================
    # PARSE
    # ==========================================================
    #

    def parse(self, tokens):

        runtime = PredictiveRuntime(
            self
        )

        return runtime.parse(tokens)

    #
    # ==========================================================
    # DEBUG
    # ==========================================================
    #

    def print_table(self):

        print(
            "========== LL(1) TABLE =========="
        )

        for key in sorted(
            self.parsing_table
        ):

            non_terminal, terminal = key

            productions = self.parsing_table[key]

            print(
                f"M[{non_terminal}, {terminal}] = "
                f"{productions}"
            )

    #
    # ==========================================================
    # TABLE ACCESS
    # ==========================================================
    #

    def get_table_entry(
        self,
        non_terminal,
        terminal
    ):

        return self.parsing_table.get(
            (non_terminal, terminal),
            set()
        )