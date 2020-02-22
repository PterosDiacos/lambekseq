'''Utilities for partial order objects.
'''

class PartialOrder:
    def __init__(self, nodes, edges):
        self.nodes = nodes.copy()
        self.edges = edges.copy()


    def restrict(self, nodes):
        self.nodes &= nodes
        self.edges = {(x, y) for x, y in self.edges if x in nodes and y in nodes}


    def addEdge(self, u, v):
        assert {u, v} <= self.nodes
        if (u, v) not in self.edges:
            self.edges.add((u, v))
            toU = {x for x in self.nodes if (x, u) in self.edges}
            fromV = {y for y in self.nodes if (v, y) in self.edges}
            self.edges.update({(x, y) for x in toU for y in fromV})


    def isAcyclic(self):
        return not any((n, n) in self.edges for n in self.nodes)

    @staticmethod
    def __transitiveClose(nodes, edges):
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    if (i, k) in edges and (k, j) in edges:
                        edges.add((i, j))

    @classmethod
    def fromPairs(cls, pairs):
        nodes = {x for x, y in pairs} | {y for x, y in pairs}
        edges = set(pairs)
        cls.__transitiveClose(nodes, edges)
        return cls(nodes, edges)


    @staticmethod
    def seqToPairs(seq):
        nodes = list(seq)
        edges = set()
        for n, i in enumerate(nodes):
            for k in range(n + 1, len(nodes)):
                edges.add((i, nodes[k]))
        return edges


    def __or__(self, other):
        nodes = self.nodes | other.nodes
        edges = self.edges | other.edges
        self.__transitiveClose(nodes, edges)
        return PartialOrder(nodes, edges)


    def __sub__(self, other):
        return self.edges - other.edges


    def __len__(self):
        return len(self.edges)


    def __contains__(self, e):
        return e in self.edges


    def __eq__(self, other):
        return self.edges == other.edges


    def __hash__(self):
        return hash(frozenset(self.edges))

    
    def __repr__(self):
        return str(self.edges)
