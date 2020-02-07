'''Continuized CCG with generalized application, lifting and lowering.
'''
from collections import defaultdict
from lambek import catIden
from parentheses import bipart, isatomic


class ReductionError(Exception): pass


def reduce(x:str, y:str) -> str:
    xslash = yslash = None    
    
    if not isatomic(x):
        xslash, xleft, xright = bipart(x)
        xleft, xright = xleft[0], xright[0]

    if not isatomic(y):
        yslash, yleft, yright = bipart(y)
        yleft, yright = yleft[0], yright[0]

    if xslash == '/':
        iden, pairs = catIden(xright, y)
        if iden: return xleft, pairs
    
    if yslash == '\\':
        iden, pairs = catIden(x, yleft)
        if iden: return yright, pairs
    
    if yslash == '/':
        res, pairs = reduce(x, yleft)
        return '(%s)/(%s)' % (res, yright), pairs

    elif yslash == '\\':
        res, pairs = reduce(x, yright)
        return '(%s)\\(%s)' % (yleft, res), pairs

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
            if not x.isPlain():
                res |= {Result(cat=r.cat + x.lastLevel, links=r.links) 
                        for r in Result._combine(x.interior(), y)}
            if not y.isPlain():
                res |= {Result(cat=r.cat + y.lastLevel, links=r.links) 
                        for r in Result._combine(x, y.interior())}
        return res

    def __add__(self, others):
        return self._combine(self, others)


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
