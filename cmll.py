''' Utilities for Cyclic Multiplicative Linear Logic (CMLL).
'''
from collections import defaultdict

from lambek import atomicIden
from parentheses import bipart, isatomic
from porder import PartialOrder


Par = 'P'
Tensor = 'T'


def isNeg(x): return '~' in x


def negIden(x, y):
    return atomicIden(x, y) and (isNeg(x) ^ isNeg(y)) 
    

def Neg(fm):
    '''CMLL negation'''
    if isinstance(fm, str):
        return '~' + fm if not isNeg(fm) else fm.replace('~', '')
    else:
        if fm[1] == Tensor:
            return (Neg(fm[2]), Par, Neg(fm[0]))
        elif fm[1] == Par:
            return (Neg(fm[2]), Tensor, Neg(fm[0]))


def cat2cmll(s: str):
    '''product-free Lambek category -> CMLL formula'''
    if isatomic(s):
        return s
    else:
        slash, left, right = bipart(s)
        left, right = left[0], right[0]
        if slash == '/':
            return (cat2cmll(left), Par, Neg(cat2cmll(right)))
        else:
            return (Neg(cat2cmll(left)), Par, cat2cmll(right))


def labelCmll(fm, natom, nconn):
    '''Return the labeled formula, and the numbers of atoms and connectives seen so far'''
    if isinstance(fm, str):
        return dict(fm=dict(symbol=fm, alab=natom), 
                    natom=natom + 1, nconn=nconn)
    else:
        left = labelCmll(fm[0], natom, nconn)
        right = labelCmll(fm[2], left['natom'], left['nconn'] + 1)
        return dict(fm=(left['fm'], 
                        dict(symbol=fm[1], clab=left['nconn'] + 1), 
                        right['fm']),
                    natom=right['natom'], nconn=right['nconn'])


class Parse:
    def __init__(self, po, ends=(), links=frozenset()):
        self.po = po
        self.ends = ends
        self.links = links

    def __eq__(self, other):
        return self.links == other.links

    def __hash__(self):
        return hash(self.links)

    def __repr__(self):
        return str(self.links)


class ProofNet:
    def __init__(self, fm):
        D = labelCmll(fm, 0, 0)
        self.fm = fm
        self.labFm, self.natom, self.nconn = D['fm'], D['natom'], D['nconn']        
        self.adict = {}                        # alab to symbol
        self.cdict = {0: Par}                  # clab to symbol
        self.cAnces = {0: []}                  # ancestors of connectives 
        self.aAnces = {}                       # ancestors of atoms
        self.po = set()
        self.__prepare(self.labFm, [0])
        self.mca = {(i, j): self.__minCommonAnces(self.aAnces[i], self.aAnces[j]) 
                    for i in self.adict for j in self.adict}
           
    def __prepare(self, fm, trace):
        if 'alab' in fm:
            self.adict[fm['alab']] = fm['symbol']
            self.aAnces[fm['alab']] = trace
        else:
            self.cdict[fm[1]['clab']] = fm[1]['symbol']
            self.cAnces[fm[1]['clab']] = trace
            for x in trace: 
                self.po.add((fm[1]['clab'], x))
            self.__prepare(fm[0], [fm[1]['clab']] + trace)
            self.__prepare(fm[2], [fm[1]['clab']] + trace)

    @classmethod
    def fromLambekCat(cls, s):
        return cls(cat2cmll(s))

    @classmethod
    def fromLambekSeq(cls, con: str, pres: list):
        fm = cat2cmll(con)
        for p in pres:
            fm = (Neg(cat2cmll(p)), Par, fm)
        return cls(fm)

    @property
    def proofCount(self):
        return len(self.proofSpan[0, self.natom - 1])

    def printProofLinks(self, symbolOnly=False):
        a = lambda x, y: ((self.adict[x], self.adict[y])
                          if isNeg(self.adict[x]) else
                          (self.adict[y], self.adict[x]))

        for parse in self.proofSpan[0, self.natom - 1]:
            if not symbolOnly: print(parse)
            s = sorted('(%s, %s)' % a(x, y) for x, y in parse.links)
            print(', '.join(s), end='\n\n')

    @staticmethod
    def __minCommonAnces(seq1, seq2):
        for x in seq1:
            if x in seq2: return x
        else:
            raise Exception('Disjoint sequences given.')

    def __TPSplit(self, conns):
        return ({c for c in conns if self.cdict[c] == Tensor}, 
                {c for c in conns if self.cdict[c] == Par})

    def buildProofs(self):
        self.po = PartialOrder(set(self.cdict), self.po)
        span = defaultdict(set)

        for step in range(1, self.natom, 2):
            for i in range(self.natom - step):
                k = i + step

                if negIden(self.adict[i], self.adict[k]):
                    if step == 1:
                        adjacentCase = {Parse(PartialOrder(self.po.nodes, self.po.edges))}
                    else:
                        adjacentCase = set()

                    for parse in span[i + 1, k - 1] | adjacentCase:
                        ends = (i,) + parse.ends + (k,)
                        links = parse.links | {(i, k)}

                        inConn = {self.mca[ends[i], ends[i + 1]] for i in range(0, len(ends) - 1, 2)}
                        inTensors, inPars = self.__TPSplit(inConn)
                        if inPars:
                            inPar = inPars.pop()                        
                            if not inPars:
                                newEdges = {(t, inPar) for t in inTensors}
                                newPo = PartialOrder(parse.po.nodes, parse.po.edges)
                                for u, v in newEdges:
                                    if (v, u) in newPo:
                                        break
                                    else:
                                        newPo.addEdge(u, v)
                                else:
                                    span[i, k].add(Parse(newPo, (i, k), links))
                      
                for j in range(i + 1, k - 1, 2):
                    for parse1 in span[i, j]:
                        for parse2 in span[j + 1, k]:
                            ends = parse1.ends + parse2.ends
                            links = parse1.links | parse2.links
                            
                            for parse in span[i, k]:
                                if links == parse.links: break
                            
                            else:
                                newEdges = parse2.po - parse1.po
                                newPo = PartialOrder(parse1.po.nodes, parse1.po.edges)
                                for u, v in newEdges:
                                    if (v, u) in newPo:
                                        break
                                    else:
                                        newPo.addEdge(u, v)
                                else:
                                    po = newPo
                                    if step < self.natom - 1:
                                        span[i, k].add(Parse(po, ends, links))
                                        
                                    else:
                                        exConn = {self.mca[ends[i], ends[i + 1]] for i in range(1, len(ends) - 2, 2)}
                                        exTensors, exPars = self.__TPSplit(exConn)
                                        exPars.add(0)
                                        if len(exPars) == 1:
                                            newEdges = {(t, 0) for t in exTensors}
                                            newPo = PartialOrder(po.nodes, po.edges)
                                            for u, v in newEdges:
                                                if (v, u) in newPo:
                                                    break
                                                else:
                                                    newPo.addEdge(u, v)
                                            else:
                                                span[i, k].add(Parse(newPo, ends, links))

        self.proofSpan = span


def selfTest():
    import pprint
    sep = '-' * 10
    print(sep + 'Test 1' + sep)
    fm = (('~p', Tensor, ((('q', Par, ('~s', Tensor, 's')), Tensor, '~s'), Par, 's')), Par, 
         (((('~s', Tensor, 's'), Par, ('~s', Par, 's')), Tensor, '~q'), Par, 'p'))
    pprint.pprint(fm)
    print()
    pn = ProofNet(fm)
    pn.buildProofs()
    pn.printProofLinks()
    print('Total: %d\n' % pn.proofCount)

    print(sep + 'Test 2' + sep)
    con, *pres = 's_0', 's_1/(np_2\\s_3)', '(np_4\\s_5)/np_6', '(s_7/np_8)\\s_9'
    pn = ProofNet.fromLambekSeq(con, pres)
    pprint.pprint(pn.fm)
    print()
    pn.buildProofs()
    pn.printProofLinks()
    print('Total: %d\n' % pn.proofCount)


if __name__ == '__main__':
    selfTest()
