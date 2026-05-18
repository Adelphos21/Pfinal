class SyntaxTreeSerializer:

    @staticmethod
    def serialize(tree):

        if tree is None:

            return None

        return (
            SyntaxTreeSerializer
            .serialize_node(
                tree.root
            )
        )

    @staticmethod
    def serialize_node(node):

        return {

            "symbol":
                node.symbol,

            "children": [

                SyntaxTreeSerializer
                .serialize_node(child)

                for child
                in node.children
            ]
        }