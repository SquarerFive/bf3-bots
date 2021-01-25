from typing import Union

# eventually move to this system (as a graph UI is in development)

EQUAL = 0
MORE = 1
LESS = 2
MORE_EQ = 3
LESS_EQ = 4


class BGraph:
    # context : any
    def __init__(self, context : object):
        self.context = context
        self.nodes = []

    def run(self, bot : object):
        pass
    
    def compute_node(self, index : int) -> Union[float, bool, str]:
        return self.nodes[index].compute()


class BGraphNode:
    def __init__(self, graph : BGraph):
        self.graph = graph
        self.type = 0
        self.dependencies = [] # int[]
        self.exposed = [] # str[]

    def compute(self):
        return 0.0

class BGraphConditionNode(BGraphNode):
    def __init__(self, graph : BGraph):
        super().__init__(graph)
        self.type = 1
        self.op = EQUAL
    
    def compute(self):
        ip0 = self.graph.compute_node(self.dependencies[0])
        ip1 = self.graph.compute_node(self.dependencies[1])
        if self.op == EQUAL:
            return ip0 == ip1
        elif self.op == MORE:
            return ip0 > ip1
        elif self.op == LESS:
            return ip0 < ip1
        elif self.op == MORE_EQ:
            return ip0 >= ip1
        elif self.op == LESS_EQ:
            return ip0 <= ip1
        