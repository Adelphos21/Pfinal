class ParserError(Exception):
    pass


#
# ==========================================================
# LR ERROR
# ==========================================================
#

class LRUnexpectedTokenError(ParserError):

    def __init__(
        self,
        state,
        token
    ):

        super().__init__(
            f"Unexpected token '{token}' "
            f"in state {state}"
        )


#
# ==========================================================
# LL1 ERROR
# ==========================================================
#

class LL1UnexpectedTokenError(ParserError):

    def __init__(
        self,
        non_terminal,
        token
    ):

        super().__init__(
            f"Unexpected token '{token}' "
            f"while parsing '{non_terminal}'"
        )