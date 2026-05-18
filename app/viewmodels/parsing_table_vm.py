class ParsingTableViewModel:

    #
    # ==========================================================
    # LR
    # ==========================================================
    #

    @staticmethod
    def build_lr(data):

        action_table = {}

        goto_table = {}

        #
        # action
        #

        for row in data["action"]:

            state = str(
                row["state"]
            )

            if state not in action_table:

                action_table[state] = {}

            #
            # conservar accept
            #

            action_table[state][
                row["symbol"]
            ] = row["actions"]

        #
        # goto
        #

        for row in data["goto"]:

            state = str(
                row["state"]
            )

            if state not in goto_table:

                goto_table[state] = {}

            goto_table[state][
                row["symbol"]
            ] = row["target"]

        return {

            "action_table":
                action_table,

            "goto_table":
                goto_table
        }

    #
    # ==========================================================
    # LL1
    # ==========================================================
    #

    @staticmethod
    def build_ll1(data):

        table = {}

        for row in data:

            non_terminal = (
                row["non_terminal"]
            )

            if non_terminal not in table:

                table[
                    non_terminal
                ] = {}

            table[
                non_terminal
            ][
                row["terminal"]
            ] = row["productions"]

        return table