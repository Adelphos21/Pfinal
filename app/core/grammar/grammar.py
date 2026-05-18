from dataclasses import dataclass

from app.core.grammar.production import Production
from app.utils.constants import EPSILON, AUGMENTED_SYMBOL


@dataclass
class Grammar:

    productions: list[Production]
    terminals: set[str]
    non_terminals: set[str]
    start_symbol: str
    augmented_start_symbol: str | None = None

    @classmethod
    def from_string(cls, grammar_text: str):

        lines = [line.strip() for line in grammar_text.strip().splitlines() if line.strip()]

        productions = []

        non_terminals = set()

        # detect non terminals

        for line in lines:

            left, _ = line.split("->")

            non_terminals.add(left.strip())

        # build productions

        production_id = 1

        for line in lines:

            left, right = line.split("->")

            left = left.strip()

            alternatives = right.split("|")

            for alternative in alternatives:

                symbols = alternative.strip().split()

                if symbols == [EPSILON]:
                    symbols = []
                
                productions.append(
                    Production(
                        id=production_id,
                        left=left,
                        right=tuple(symbols)
                    )
                )
                production_id += 1

        # terminals

        terminals = set()

        for production in productions:

            for symbol in production.right:

                if symbol not in non_terminals and symbol != EPSILON:
                    terminals.add(symbol)

        start_symbol = productions[0].left

        grammar = cls(
            productions=productions,
            terminals=terminals,
            non_terminals=non_terminals,
            start_symbol=start_symbol
        )

        grammar.validate()

        return grammar

    def validate(self):

        if not self.productions:
            raise ValueError("Grammar has no productions")

        if not self.start_symbol:
            raise ValueError("Grammar has no start symbol")

    def get_productions_for(self, non_terminal: str):

        return [production for production in self.productions if production.left == non_terminal]

    def get_production_by_id(self, production_id):

        for production in self.productions:

            if production.id == production_id:
                return production

        raise ValueError(
            f"Production {production_id} not found"
        )

    def augment(self):

        augmented_symbol = self.start_symbol + AUGMENTED_SYMBOL

        augmented_production = Production(id=0, left=augmented_symbol, right=(self.start_symbol,))

        self.productions.insert(0, augmented_production)

        self.non_terminals.add(augmented_symbol)

        self.augmented_start_symbol = augmented_symbol