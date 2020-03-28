'''Continuized CCG with generalized application, lifting and lowering.
'''
from collections import defaultdict

from lambekseq.lbnoprod import usecache
from lambekseq.lib.cterm import bipart, isatomic, catIden
from lambekseq.lib.cterm import unslash, addHypo


Conns = {'/', '\\', '^', '!'}


class Result:
    def __init__(self, cat:str, links=frozenset()):
        self.cat = cat
        self.links = links

    def __iter__(self):
        return iter(self.links)

    def __eq__(self, other):
        return (self.cat == other.cat
            and self.links == other.links)

    def __hash__(self):
        return hash((self.cat, self.links))

    def __repr__(self):
        return self.cat

    def __add__(self, others):
        return reduce(self, others)

    @staticmethod
    def _lowering(s:str):
        a, d, e = towerSplit(s)
        if not d: 
            return a, frozenset()
        else:
            c, pairs = Result._lowering(a)
            iden, more = catIden(c, e)
            if iden:
                return d, pairs | more
            else:
                s = addHypo(e, '^', c)
                s = addHypo(d, '!', s)
                return s, pairs

    def collapse(self):
        '''Recursive lowering.'''
        cat, pairs = self._lowering(self.cat)
        self.cat = cat
        self.links |= pairs


@usecache
def towerSplit(x:str, conn={'/', '\\', '^', '!'}):
    '''Split a tower of `((b^c)!a)` into `(c, a, b)`.'''
    if isatomic(x, conn=conn):
        return (x, None, None)
    else:
        _, l, a = bipart(x, conn=conn, noComma=True)
        if _ in {'/', '\\'}:
            return (x, None, None)
        else:
            _, b, c = bipart(l, conn=conn, noComma=True)
            return (c, a, b)


def propogate(xlist, ylist, i, j, cat):
    '''Propogate a reduction at cell (i, j) back to (0, 0).'''
    for k in range(j, -1, -1):
        cat = addHypo(cat, *ylist[k][1:])
    for k in range(i, -1, -1):
        cat = addHypo(cat, *xlist[k][1:])
    return cat


def cellAppl(xlist, ylist, i, j, slash):
    try:
        if xlist[i + 1][1] == slash:
            iden, pairs = catIden(xlist[i + 1][2], ylist[j][0])
            if iden:
                cat = propogate(xlist, ylist, i, j, xlist[i + 1][0])  
                return {Result(cat, pairs)}
    except IndexError:
        pass
    
    try:
        if j == len(ylist) - 1:
            c, a, b = towerSplit(ylist[j][0])
            if a:
                if slash == '/':
                    res = reduce(Result(xlist[i][0]), Result(c))
                elif slash == '\\':
                    res = reduce(Result(c), Result(xlist[i][0]))                
                for r in res:
                    iden = False
                    if r._earlyCollapse:
                        iden, pairs = catIden(b, r.cat)
                    if iden:
                        r.links |= pairs
                        r.cat = a
                    else:
                        r.cat = addHypo(b, '^', r.cat)
                        r.cat = addHypo(a, '!', r.cat)
                    r.cat = propogate(xlist, ylist, i, j, r.cat)
                return {r for r in res}
    except IndexError:
        pass
    
    return set()


def reduce(x:Result, y:Result) -> set:
    '''Use only the 0-th row and 0-th column of the reduction table'''
    xlist, ylist = unslash(x.cat), unslash(y.cat)
    
    res = set()
    for s in range(len(xlist) + len(ylist) - 1):
        for i in range(s, -1, -1):
            j  = s - i
            if i and j: continue
            res.update(cellAppl(xlist, ylist, i, j, '/'))
            res.update(cellAppl(ylist, xlist, j, i, '\\'))

        if res: break
    
    xyLinks = x.links | y.links
    for r in res: r.links |= xyLinks
    return {r for r in res}


class Cntccg:
    def __init__(self, con:str, pres:list, earlyCollapse=True):
        self.con = con
        self.pres = list(pres)
        Result._earlyCollapse = earlyCollapse

    def __len__(self):
        return len(self.pres)

    @property
    def allProofs(self):
        return self._proofSpan[0, len(self) - 1]

    @property
    def proofs(self):
        return list(filter(lambda r: catIden(r.cat, self.con)[0], 
                    self.allProofs))

    @property
    def proofCount(self, matchCon=True):
        return len(self.proofs if matchCon else self.allProofs)

    def printProofs(self, matchCon=True):
        pool = self.proofs if matchCon else self.allProofs
        for r in pool:
            if matchCon: r.links |= catIden(r.cat, self.con)[1]
            s = sorted('(%s, %s)' % (i, j) for i, j in r.links)
            print(', '.join(s))
        if pool: print()

    def parse(self):
        '''CKY parsing.'''
        span = defaultdict(set)
        for i in range(len(self)):
            span[i, i] = {Result(self.pres[i])}

        for step in range(1, len(self)):
            for i in range(len(self) - step):
                k = i + step
                for j in range(i + 1, k + 1):
                    for x in span[i, j - 1]:
                        for y in span[j, k]:
                            span[i, k].update(x + y)

        if not Result._earlyCollapse:
            res = span[0, len(self) - 1]
            for r in res: r.collapse()
            res = {r for r in res}

        self._proofSpan = span


def selfTest():
    from lambekseq.lib.cindex import indexSeq

    con, *pres = 's', '(s^np)!s', '(np\\s)/np', '(s^np)!s', '(s\\s)/np', '(s^np)!s'
    (con, *pres), _ = indexSeq(con, pres)        
    cntccg = Cntccg(con, pres, earlyCollapse=False)
    cntccg.parse()
    cntccg.printProofs()
    print('Total:', cntccg.proofCount)


if __name__ == '__main__':
    selfTest()
