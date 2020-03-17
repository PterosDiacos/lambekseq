'''Product-free Lambek sequent calculus. 
This script finds the axioms of every proof.
'''
from lambekseq.lib.cterm import isatomic, bipart, atomicIden


def addcache(f):
    f._cache = dict()
    return f


@addcache
def cachedproof(*args):
    if args not in cachedproof._cache:
        cachedproof._cache[args] = findproof(args[0], *args[1:])
    return cachedproof._cache[args]


def find_diffTV(con, pres, cut, left, right):
    U = pres[:cut]
    alts = set()
    for j in range(cut + 1, len(pres) + 1):
        T, V = pres[cut + 1:j], pres[j:]
        rightproof = cachedproof(right, *T)
        if rightproof:
            leftproof = cachedproof(con, *U, left, *V)
            if leftproof:
                alts.update({r | l for r in rightproof 
                                   for l in leftproof}) 
    return alts


def find_diffUT(con, pres, cut, left, right):
    V = pres[cut + 1:]
    alts = set()
    for j in range(cut + 1):
        U, T = pres[:j], pres[j:cut]
        leftproof = cachedproof(left, *T)
        if leftproof:
            rightproof = cachedproof(con, *U, right, *V)
            if rightproof:
                alts.update({l | r for l in leftproof
                                   for r in rightproof})
    return alts


def findproof(con, *pres):
    '''Find proofs by showing the axiomatic premises.'''
    # when the conclusion is non-atomic
    if not isatomic(con):
        slash, left, right = bipart(con, noComma=True)
        if slash == '/':
            return cachedproof(left, *pres, right)
        elif slash == '\\':
            return cachedproof(right, left, *pres)

    # when the conclusion is atomic
    else:
        if len(pres) == 0:
            return set()
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
    def __init__(self, con, pres):
        self.con = con
        self.pres = pres

    def parse(self):
        self.proofs = findproof(self.con, *self.pres)

    @property
    def proofCount(self):
        return len(self.proofs)

    def printProofs(self):
        for p in self.proofs:
            s = sorted('(%s, %s)' % (i, j) for (i, j) in p)
            print(', '.join(s))        
        if self.proofs: print()


def selfTest():
    from lambekseq.lib.cindex import indexSeq
    con, *pres = 's', 's/(np\\s)', '(np\\s)/np', '(s/np)\\s'
    (con, *pres), _ = indexSeq(con, pres)
    lbk = LambekProof(con, pres)
    lbk.parse()
    lbk.printProofs()


if __name__ == '__main__':
    selfTest()
