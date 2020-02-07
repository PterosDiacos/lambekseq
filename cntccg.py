'''Continuized CCG with application, composition, Lifting and Lowering.
'''
from collections import defaultdict
from lambek import catIden
from parentheses import bipart, isatomic


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

    def reduceLevel(self):
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


def baseCombine(x: Result, y: Result) -> {Result}:
    xslash = yslash = None

    if not isatomic(x[0]):
        xslash, xleft, xright = bipart(x[0])
        xleft, xright = xleft[0], xright[0]
    
    if not isatomic(y[0]):
        yslash, yleft, yright = bipart(y[0])
        yleft, yright = yleft[0], yright[0]
        
    if xslash == '/':
        iden, pairs = catIden(xright, y[0])
        if iden:
            # forward application
            resCat = xleft

        elif yslash == '/':
            iden, pairs = catIden(xright, yleft)
            if iden: 
                # forward composition
                resCat = '(%s)/(%s)' % (xleft, yright)    
    elif yslash == '\\':
        iden, pairs = catIden(x[0], yleft)
        if iden:
            # backward application
            resCat = yright

        elif xslash == '\\':
            iden, pairs = catIden(xright, yleft)
            if iden:
                # backward composition
                resCat = '(%s)\\(%s)' % (xleft, yright)

    try:
        return {Result(cat=(resCat,), 
                       links=x.links | y.links | pairs)}
    except NameError:
        return set()


def combine(x:Result, y:Result) -> {Result}:
    if x.isPlain() and y.isPlain():
        res = baseCombine(x, y)
    else:
        res = set()
        if not x.isPlain():
            res |= {Result(cat=r.cat + x.lastLevel, links=r.links) 
                    for r in combine(x.reduceLevel(), y)}
        if not y.isPlain():
            res |= {Result(cat=r.cat + y.lastLevel, links=r.links) 
                    for r in combine(x, y.reduceLevel())}
    return res


class Cntccg:
    def __init__(self, seq):
        self.seq = list(seq)

    def __len__(self):
        return len(self.seq)

    @property
    def proofCount(self):
        return len(self.proofs)

    def printProofs(self):
        for r in self.proofs:
            s = sorted('(%s, %s)' % (i, j) for i, j in r.links)
            print('%-8s' % r[0], ', '.join(s))

    def parse(self):
        '''CYK parsing.'''
        span = defaultdict(set)
        for i in range(len(self)):
            span[i, i] = {Result(self.seq[i])}

        for step in range(1, len(self)):
            for i in range(len(self) - step):
                k = i + step
                for j in range(i + 1, k + 1):
                    for x in span[i, j - 1]:
                        for y in span[j, k]:
                            span[i, k] |= combine(x, y)
        
        self.proofs = span[0, len(self) - 1]
        for r in self.proofs: r.collapse()


def selfTest():
    # [every boy] walked [most dogs] in [every park]
    seq = [
        ('np_0', ('s_1', 's_2')),
        ('(np_3\\s_4)/np_5',),
        ('np_6', ('s_7', 's_8')),
        ('((np_9\\s_10)\\(np_11\\s_12))/np_13',),
        # ('(s_10\\s_12)/np_13',),
        ('np_14', ('s_15', 's_16'))
    ]
    cntccg = Cntccg(seq)
    cntccg.parse()
    cntccg.printProofs()
    print('Total:', cntccg.proofCount)

    print('\n' + '-' * 10 + '\n')

    # hypothetical 4-place predicate
    seq = [
        ('(((s_0/np_1)/np_2)/np_3)/np_4',),
        ('np_5', ('s_6', 's_7')),
        ('np_8', ('s_9', 's_10')),
        ('np_11', ('s_12', 's_13')),
        ('np_14', ('s_15', 's_16'))
    ]
    cntccg = Cntccg(seq)
    cntccg.parse()
    cntccg.printProofs()
    print('Total:', cntccg.proofCount)


if __name__ == '__main__':
    selfTest()
