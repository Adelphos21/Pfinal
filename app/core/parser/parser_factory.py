from app.core.parsing.lr.lr0 import LR0
from app.core.parsing.lr.slr1 import SLR1
from app.core.parsing.lr.lr1 import LR1
from app.core.parsing.lr.lalr1 import LALR1
from app.core.parsing.topdown.ll1 import LL1

class ParserFactory:

    @staticmethod
    def create(
        parser_type,
        grammar
    ):

        parser_type = parser_type.lower()

        #
        # LL1
        #

        if parser_type == "ll1":

            return LL1(grammar)

        #
        # LR0
        #

        if parser_type == "lr0":

            return LR0(grammar)

        #
        # SLR1
        #

        if parser_type == "slr1":

            return SLR1(grammar)

        #
        # LR1
        #

        if parser_type == "lr1":

            return LR1(grammar)

        #
        # LALR1
        #

        if parser_type == "lalr1":

            return LALR1(grammar)

        #
        # unknown parser
        #

        raise ValueError(
            f"Unknown parser type: "
            f"{parser_type}"
        )