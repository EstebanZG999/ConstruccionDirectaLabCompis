# mock_syntax_tree.py
class MockNode:
    def __init__(self, node_type, symbol=None, position=None,
                 firstpos=None, lastpos=None, children=None):
        self.type = node_type  # 'LEAF', 'CONCAT', 'KLEENE', 'UNION', etc.
        self.symbol = symbol
        self.position = position
        self.firstpos = firstpos or set()
        self.lastpos = lastpos or set()
        self.children = children or []

    def is_leaf(self):
        return self.type == 'LEAF'

    @property
    def left(self):
        return self.children[0] if self.children else None

    @property
    def right(self):
        return self.children[1] if len(self.children) > 1 else None

def build_mock_tree_for_ab_star_hash():
    """
    Construye manualmente un árbol que represente (a|b)*#
    con posiciones, firstpos, lastpos y followpos ya calculados.
    """
    # Hojas
    leaf_a = MockNode(
        node_type='LEAF',
        symbol='a',
        position=1,
        firstpos={1},
        lastpos={1}
    )
    leaf_b = MockNode(
        node_type='LEAF',
        symbol='b',
        position=2,
        firstpos={2},
        lastpos={2}
    )
    leaf_hash = MockNode(
        node_type='LEAF',
        symbol='#',
        position=3,
        firstpos={3},
        lastpos={3}
    )

    # Union (a|b)
    union_ab = MockNode(
        node_type='UNION',
        firstpos={1, 2},
        lastpos={1, 2},
        children=[leaf_a, leaf_b]
    )

    # (a|b)*
    kleene_ab = MockNode(
        node_type='KLEENE',
        firstpos={1, 2},
        lastpos={1, 2},
        children=[union_ab]
    )

    # CONCAT( (a|b)* , # )
    concat = MockNode(
        node_type='CONCAT',
        firstpos={1, 2},
        lastpos={3},
        children=[kleene_ab, leaf_hash]
    )

    return concat
