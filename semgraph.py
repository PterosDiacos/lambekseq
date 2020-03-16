'''Semantic Graphs (Semgraphs).'''
import graphviz
import networkx as nx
from copy import deepcopy
from lib.totikz import totikz


DEFAULT_STYLING = dict(graph_attr=dict(overlap='scale', layout='neato'),
                       edge_attr=dict(arrowhead='vee', arrowsize='0.5',
                                      fontsize='12', color='grey'),
                       node_attr=dict(shape='circle', margin='0', 
                                      width='0.1', height='0.1',
                                      fontsize='12'))


class Semgraph(nx.DiGraph):
    '''Node prefixes:  
        - 'a': active sources  
        - 'i': inactive sources  
        - 'x': referencing and scoping sources  
        - 'u': fictious nodes for creating unary edges
    '''

    def __init__(self, *pargs, **kargs):
        self.toknum = kargs.get('toknum')
        self.cat = kargs.get('cat')
        self.sort = kargs.get('sort')        
        nx.DiGraph.__init__(self, *pargs, **kargs)


    @classmethod
    def from_dict(cls, D, filler='', toknum=None, extra=0):
        '''D has the following keys:
            - 'toknum':   the token number (ID).
            - 'cat':      the syntactic category of the graph. Abbreviations can be used.  
            - 'sort':     the semantic sort of the graph, i.e. the number of active sources.  
            - 'named':    a list of (SOURCE, LABEL) pairs for nodes bearing a unary label.  
            - 'anonyms':  a list of SOURCE for anonymous nodes.  
            - 'arrows':   a list of (FROM, TO, LABEL) triples for edges tailed at FROM,
                          headed to TO, and labeled as LABEL.
        '''
        D = deepcopy(D)
        D.setdefault('cat', None)
        D.setdefault('sort', 0)
        D.setdefault('anonyms', [])
        D.setdefault('named', [])
        D.setdefault('arrows', [])

        for pair in D['named']:
            if not pair[1]: 
                pair[1] = filler
                break
        else:
            for triple in D['arrows']:
                if not triple[2]:
                    triple[2] = filler
                    break

        sg = cls(toknum=toknum, cat=D['cat'], sort=D['sort'])
        sg.add_anonyms_from(D['anonyms'])
        sg.add_named_from(D['named'])
        sg.add_arrows_from(D['arrows'])
        return sg


    def conj_expand(self, idxDict):
        '''Add `a`-prefix-sources according to the expanded category of `self`.
        Return a new copy.'''
        g = deepcopy(self)
        conj_len = len([i for i, t in idxDict.toToken.items() 
                          if int(t) == self.toknum]) // 3

        for i in range(1, conj_len):
            nfrom1 = 'a%d' % (2 + i)
            nfrom2 = 'a%d' % (1 + i + conj_len)
            nto = 'a%d' % (i + 2 * conj_len)
            g.add_anonyms_from([nfrom1, nfrom2, nto])
            g.add_arrows_from([[nfrom1, nto, '='],
                               [nfrom2, nto, '=']])
        
        g.sort += 3 * (conj_len - 1)
        return g


    def add_xsource(self, xsrc):
        '''Add one `x`-prefix-source.
        `self` should be pronominal; `self.sort` remains unchanged'''
        if xsrc > 0:
            nfrom = 'x%d' % xsrc
            nto = 'a0' if self.cat == 'np' else 'i0'
            self.add_anonym(nfrom)
            self.add_arrow(nfrom, nto, '=')


    def add_arrow(self, nfrom, nto, label):
        '''Token numbers automatically prepended'''
        nfrom = 'g%s%s' % (self.toknum, nfrom)
        nto = 'g%s%s' % (self.toknum, nto)
        self.add_edge(nfrom, nto, xlabel=label)


    def add_anonym(self, node_for_adding):
        '''Token numbers automatically prepended'''
        nd = 'g%s%s' % (self.toknum, node_for_adding)
        self.add_node(nd, label='')


    def add_named(self, node_for_adding, unary_label):
        '''Token numbers automatically prepended'''
        nd = 'g%s%s' % (self.toknum, node_for_adding)
        ndu = 'g%su%s' % (self.toknum, node_for_adding[1:])
        self.add_node(nd, label='')
        self.add_node(ndu, label='',
                      width=0, height=0, 
                      shape='plaintext')
        self.add_edge(nd, ndu, xlabel=unary_label, len=0.5)


    def add_arrows_from(self, iterable):
        '''From a list of triples: (`from`, `to`, `label`)'''
        for nfrom, nto, label in iterable:
            self.add_arrow(nfrom, nto, label)


    def add_named_from(self, iterable):
        '''From a list of pairs: (`source`, `label`)'''
        for src, label in iterable:
            self.add_named(src, label)


    def add_anonyms_from(self, iterable):
        '''From a list of sources'''
        for src in iterable:
            self.add_anonym(src)


    def iso(self, mapping):
        return nx.relabel_nodes(self, mapping)


    @property
    def dot(self):
        return nx.drawing.nx_pydot.to_pydot(self).to_string()


    @property
    def dot_body(self):
        lines = ['\t' + l for l in self.dot.split('\n')[1:-2]]
        return '\n'.join(lines)


    @property
    def dot_styled(self, styling=DEFAULT_STYLING):
        g = graphviz.Digraph(**styling)
        g.body.append(self.dot_body)
        return g.source


    @property
    def tikz(self):
        return totikz(self.dot)
