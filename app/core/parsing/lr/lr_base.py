from abc import ABC, abstractmethod
from collections import defaultdict

from app.core.grammar.grammar import Grammar
from app.core.automata.automaton import Automaton
from app.core.parsing.lr.lr_conflict import LRConflict

from app.core.parser.abstract_parser import (
    AbstractParser
)
from app.core.parser.shift_reduce_runtime import (
    ShiftReduceRuntime
)

class LRBase(AbstractParser):

    def __init__(self, grammar: Grammar):

        self.grammar = grammar

        self.grammar.augment()

        #
        # automata
        #

        self.nfa = Automaton()

        self.dfa = Automaton()

        #
        # parsing tables
        #

        self.action_table = defaultdict(set)

        self.goto_table = {}

        #
        # conflicts
        #

        self.conflicts = []

        #
        # build everything
        #

        self.build()

    def build(self):

        self.build_nfa()

        self.build_dfa()

        self.build_parsing_table()

    #
    # action helpers
    #

    def is_shift_action(self, action: str):

        return action.startswith("s")

    def is_reduce_action(self, action: str):

        return action.startswith("r")

    def is_accept_action(self, action: str):

        return action == "accept"

    def get_shift_target(self, action: str):

        return int(action[1:])

    def get_reduce_production_id(self, action: str):

        return int(action[1:])

    #
    # conflict helpers
    #

    def detect_conflict_type(self, old_action, new_action):

        old_reduce = self.is_reduce_action(old_action)
        new_reduce = self.is_reduce_action(new_action)

        old_shift = self.is_shift_action(old_action)
        new_shift = self.is_shift_action(new_action)

        #
        # reduce/reduce
        #

        if old_reduce and new_reduce:
            return "reduce/reduce"

        #
        # shift/reduce
        #

        if (old_shift and new_reduce) or (old_reduce and new_shift):
            return "shift/reduce"

        return "unknown"

    def register_conflict(self, state, symbol, old_action, new_action):

        conflict_type = self.detect_conflict_type(old_action, new_action)

        conflict = LRConflict(
            state=state,
            symbol=symbol,
            old_action=old_action,
            new_action=new_action,
            conflict_type=conflict_type
        )

        self.conflicts.append(conflict)

    #
    # table helpers
    #

    def add_action(self, state_id, symbol, action,  register_conflict=True):
        key = (state_id, symbol)

        old_actions = self.action_table[key]

        #
        # same action
        #

        if action in old_actions:
            return

        #
        # register conflicts
        #

        if register_conflict:

            for old_action in old_actions:

                self.register_conflict(
                    state=state_id,
                    symbol=symbol,
                    old_action=old_action,
                    new_action=action
                )

        #
        # store action
        #

        self.action_table[key].add(action)

    def add_goto(self, state_id, symbol, target):

        self.goto_table[(state_id, symbol)] = target



    #
    # ==========================================================
    # PARSE
    # ==========================================================
    #

    def parse(self, tokens):

        runtime = ShiftReduceRuntime(
            self
        )

        return runtime.parse(tokens)

    #
    # parser validation
    #

    @property
    @abstractmethod
    def is_valid(self):
        pass

    #
    # abstract methods
    #

    @abstractmethod
    def build_nfa(self):
        pass

    @abstractmethod
    def build_dfa(self):
        pass

    @abstractmethod
    def build_parsing_table(self):
        pass