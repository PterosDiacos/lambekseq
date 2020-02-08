'''Continuized CCG with generalized application, lifting and lowering.
'''
from collections import defaultdict
from lambek import catIden, unslash, addHypo
from parentheses import bipart, isatomic


class ReductionError(Exception): pass
            
def reduce(x:str, y:str) -> str:
    xlist, ylist = unslash(x), unslash(y)
    
    for s in range(len(xlist) + len(ylist) - 1):
        for i in range(s, -1, -1):
            j  = s - i

            # only the 1st row & the 1st column of the reduction table
            if i * j: continue

            try:
                if xlist[i + 1][1] == '/':
                    iden, pairs = catIden(xlist[i + 1][2], ylist[j][0])
                    if iden:
                        resCat = xlist[i + 1][0]                        
                        for k in range(j, -1, -1):
                            resCat = addHypo(resCat, *ylist[k][1:])
                        for k in range(i, -1, -1):
                            resCat = addHypo(resCat, *xlist[k][1:])                            
                        return resCat, pairs
            except IndexError:
                pass
            
            try:    
                if ylist[j + 1][1] == '\\':
                    iden, pairs = catIden(xlist[i][0], ylist[j + 1][2])
                    if iden:
                        resCat = ylist[j + 1][0]
                        for k in range(j, -1, -1):
                            resCat = addHypo(resCat, *ylist[k][1:])
                        for k in range(i, -1, -1):
                            resCat = addHypo(resCat, *xlist[k][1:])
                        return resCat, pairs            
            except IndexError:
                pass

    raise ReductionError


class Result:
    '''Plain category:    ('np',)    
       Tower category:    ('np', ('s', 's'), ...)
    '''    
    def __init__(self, cat:tuple, links=frozenset()):
        self.cat = cat
        self.links = links

    def __eq__(self, other):
        return (self.cat == other.cat and
                self.links == other.links)

    def __hash__(self):
        return hash((self.cat, self.links))

    def __repr__(self):
        return str(self.cat)

    def __getitem__(self, idx):
        return self.cat[idx]

    def __add__(self, others):
        return self._combine(self, others)

    @staticmethod
    def _combine(x, y):
        if x.isPlain() and y.isPlain():
            try:
                resCat, pairs = reduce(x[0], y[0])
            except ReductionError:
                return set()
            else:
                return {Result(cat=(resCat,), 
                            links=x.links | y.links | pairs)}        
        else:
            res = set()
            # lifting
            if not x.isPlain():
                res |= {Result(cat=r.cat + x.lastLevel, links=r.links) 
                        for r in Result._combine(x.interior(), y)}
            if not y.isPlain():
                res |= {Result(cat=r.cat + y.lastLevel, links=r.links) 
                        for r in Result._combine(x, y.interior())}

        return res

    def isPlain(self):
        return len(self.cat) == 1

    def interior(self):
        return Result(cat=self[:-1], links=self.links)
    
    @property
    def lastLevel(self):
        return (self[-1],)

    def collapse(self):
        '''Recursive lowering.'''
        while not self.isPlain():
            iden, pairs = catIden(self[0], self[1][1])
            if iden:
                self.links |= pairs
                self.cat = (self[1][0],) + self[2:]
            else: break


class Cntccg:
    def __init__(self, pres):
        self.pres = [self._toTower(x) for x in pres]

    @staticmethod
    def _toTower(s):
        if catIden('s/(np\\s)', s)[0] or catIden('(s/np)\\s', s)[0]:
            slash, left, right = bipart(s)
            if slash == '/':
                _, np, right = bipart(right[0])
            else:
                _, left, np = bipart(left[0])    
            return (np[0], (left[0], right[0]))
        else:
            return (s,)

    def __len__(self):
        return len(self.pres)

    def proofCount(self, con=None):
        pool = list(filter(lambda r: catIden(r[0], con)[0], 
                    self.proofs)) if con else self.proofs
        return len(pool)

    def printProofs(self, con=None):
        pool = list(filter(lambda r: catIden(r[0], con)[0], 
                    self.proofs)) if con else self.proofs
        for r in pool:
            if con: r.links |= catIden(r[0], con)[1]
            s = sorted('(%s, %s)' % (i, j) for i, j in r.links)
            print(', '.join(s))

    def parse(self):
        '''CYK parsing.'''
        span = defaultdict(set)
        for i in range(len(self)):
            span[i, i] = {Result(self.pres[i])}

        for step in range(1, len(self)):
            for i in range(len(self) - step):
                k = i + step
                for j in range(i + 1, k + 1):
                    for x in span[i, j - 1]:
                        for y in span[j, k]:
                            span[i, k] |= x + y
        
        self.proofs = span[0, len(self) - 1]
        for r in self.proofs: r.collapse()


def selfTest():
    from cindex import indexToken

    (_, *pres), _ = indexToken(
        's', ['s/(np\\s)', '(np\\s)/np', 's/(np\\s)', '(s\\s)/np', 's/(np\\s)'])
    cntccg = Cntccg(pres)
    cntccg.parse()
    cntccg.printProofs()
    print('Total:', cntccg.proofCount())


if __name__ == '__main__':
    selfTest()
