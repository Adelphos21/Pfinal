class AutomatonViewModel:

    @staticmethod
    def build(data):

        return {

            "states": [

                {
                    #
                    # identity
                    #

                    "id":
                        state["id"],

                    "label":
                        f"I{state['id']}",

                    #
                    # LR items
                    #

                    "items":
                        state["items"],

                    #
                    # initial state
                    #

                    "is_initial":
                        state["id"] == 0,

                    #
                    # accepting state
                    #

                    "is_accepting":

                        any(

                            "•," in item
                            or item.endswith("•]")
                            or item.endswith("•")

                            for item
                            in state["items"]
                        )
                }

                for state
                in data["states"]
            ],

            #
            # transitions
            #

            "transitions":
                data["transitions"]
        }