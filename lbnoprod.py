'''Product-free Lambek sequent calculus. 
This script finds the axioms of every proof.
'''
from lambekseq.lib.cterm import isatomic, bipart, atomicIden
from lambekseq.lib.tobuss import toBuss


def usecache(func):
    def onCall(*args, **kwargs):
        if args not in onCall.cache:
            onCall.cache[args] = func(*args, **kwargs)
        return onCall.cache[args]
    
    onCall.cache = dict()
    return onCall


def tracecache(func):
    def onCall(*args, **kwargs):
        res = func(*args, **kwargs)
        if res: 
            onCall.trace.append([args, list(res)])
        return res

    onCall.cache = func.cache
    onCall.trace = []
    return onCall


def find_diffTV(con, pres, cut, left, right):
    U = pres[:cut]
    alts = set()
    for j in range(cut + 1, len(pres) + 1):
        T, V = pres[cut + 1:j], pres[j:]
        rightproof = findproof(right, *T)
        if rightproof:
            leftproof = findproof(con, *U, left, *V)
            if leftproof:
                alts.update({r | l for r in rightproof 
                                   for l in leftproof}) 
    return alts


def find_diffUT(con, pres, cut, left, right):
    V = pres[cut + 1:]
    alts = set()
    for j in range(cut + 1):
        U, T = pres[:j], pres[j:cut]
        leftproof = findproof(left, *T)
        if leftproof:
            rightproof = findproof(con, *U, right, *V)
            if rightproof:
                alts.update({l | r for l in leftproof
                                   for r in rightproof})
    return alts


@tracecache
@usecache
def findproof(con, *pres):
    '''Find proofs by showing the axiomatic premises.'''
    # when the conclusion is non-atomic
    if not isatomic(con):
        slash, left, right = bipart(con, noComma=True)
        if slash == '/':
            return findproof(left, *pres, right)
        elif slash == '\\':
            return findproof(right, left, *pres)

    # when the conclusion is atomic
    else:
        altBranches = set()
        hit_nonatomic = False
        for i in range(len(pres)):
            if not isatomic(pres[i]):
                hit_nonatomic = True
                slash, left, right = bipart(pres[i], noComma=True)
                if slash == '/':
                    altBranches.update(find_diffTV(con, pres, i, left, right))
                elif slash == '\\':
                    altBranches.update(find_diffUT(con, pres, i, left, right))

        if hit_nonatomic:
            return altBranches
        else:
            if len(pres) == 1 and atomicIden(pres[0], con):
                return {frozenset({tuple(sorted({pres[0], con}))})}
            else:
                return set()


class LambekProof:
    def __init__(self, con, pres, **kwargs):
        self.con = con
        self.pres = pres

    def parse(self):
        findproof.cache.clear()
        findproof.trace.clear()
        self.proofs = findproof(self.con, *self.pres)
        self.cache = findproof.cache
        self.trace = findproof.trace

    @property
    def proofCount(self):
        return len(self.proofs)

    def printProofs(self):
        for p in self.proofs:
            s = sorted('(%s, %s)' % (i, j) for (i, j) in p)
            print(', '.join(s))        
        if self.proofs: print()

    def buildTree(self):
        tree = {}
        class ChildrenFound(Exception): pass
        for i in range(len(self.trace)):
            if len(self.trace[i][1][0]) > 1:
                for seti in self.trace[i][1]:
                    if (self.trace[i][0], seti) in tree: 
                        continue
                    try:
                        for setpre in self.trace[i - 1][1]:
                            if setpre == seti:
                                tree[self.trace[i][0], seti] = (self.trace[i - 1][0],)
                                raise ChildrenFound

                        for j in range(i - 1, -1, -1):
                            for setj in self.trace[j][1]:
                                if setj < seti:
                                    for k in range(j - 1, -1, -1):
                                        for setk in self.trace[k][1]:
                                            if seti == setj | setk:
                                                tree[self.trace[i][0], seti] = (self.trace[j][0],
                                                                                self.trace[k][0])
                                                raise ChildrenFound
                    except ChildrenFound:
                        continue
        self.tree = tree

    def printTree(self, space='.' * 4):
        def onCall(con, pres, parentLinks=None, indent=''):
            key = con, *pres
            for links in self.cache[key]:
                if parentLinks and not links <= parentLinks:
                    continue 

                if not indent:
                    s = sorted('(%s, %s)' % (i, j) for (i, j) in links)
                    print(', '.join(s) + '\n' + '-' * 10 + '\n')

                if (key, links) in self.tree:
                    for sub in self.tree[key, links]:
                        onCall(sub[0], sub[1:], links, indent + space)
                print(indent, *pres, '->', con)
                
                if not indent: print('\n')

        onCall(self.con, self.pres)

    def printBussTree(self):
        print(toBuss(self.con, self.pres, self.cache, self.tree))


def selfTest():
    from lambekseq.lib.cindex import indexSeq
    con, *pres = 's', 's/(np\\s)', '(np\\s)/np', '(s/np)\\s'
    (con, *pres), _ = indexSeq(con, pres)
    lbk = LambekProof(con, pres)
    lbk.parse()
    lbk.buildTree()
    lbk.printTree()


if __name__ == '__main__':
    selfTest()
