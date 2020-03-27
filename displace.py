'''Product-free Basic Displacement sequent calculus.
This script finds the axioms of every proof.
Write `^` for upward arrow, '!' for downward arrow, '-' for gap.
'''
from lambekseq.lib.cterm import atomicIden as _atomicIden
from lambekseq.lib.cterm import bipart, isatomic
from lambekseq.lbnoprod import usecache
from lambekseq.lbnoprod import LambekProof as _LambekProof


Gap = '-'
Conns = {'/', '\\', '^', '!'}


def atomicIden(x, y):
    if Gap in {x, y}:
        return x == y
    else:
        return _atomicIden(x, y)


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


def find_extract(con, pres, cut, left, right):
    alts = set()
    for i in range(cut, -1, -1):
        for j in range(cut, len(pres)):
            if not pres[i:j + 1].count(Gap):
                rightproof = findproof(con, *pres[:i], right, *pres[j + 1:])
                if rightproof:
                    leftproof = findproof(left, *pres[i:cut], Gap, *pres[cut + 1:j + 1])
                    if leftproof:
                        alts.update({l | r for l in leftproof
                                           for r in rightproof})
    return alts


@usecache
def findproof(con, *pres):
    pres = list(pres)

    # when the conclusion is non-atomic
    if not isatomic(con, conn=Conns):
        conn, left, right = bipart(con, conn=Conns, noComma=True)
        if conn == '/':
            return findproof(left, *pres, right)        
        elif conn == '\\':
            return findproof(right, left, *pres)
        elif conn == '!':
            return findproof(right, left, *pres).union(
                   findproof(right, *pres, left))
        elif conn == '^':
            try:
                assert pres.count(Gap) <= 1
                cut = pres.index(Gap)
            except AssertionError:
                return set()
            except ValueError:
                alts = set()
                for i in range(len(pres) + 1):
                    alts.update(findproof(con, *pres[:i], Gap, *pres[i:]))
                return alts
            else:
                return findproof(left, *pres[:cut], right, *pres[cut + 1:])
                    
    # when the conclusion is atomic
    else:
        if len(pres) == 0:
            return set()
        else:
            altBranches = set()
            hit_nonatomic = False
            for i in range(len(pres)):
                if not isatomic(pres[i], conn=Conns):
                    hit_nonatomic = True
                    conn, left, right = bipart(pres[i], conn=Conns, noComma=True)
                    if conn == '/':
                        altBranches.update(find_diffTV(con, pres, i, left, right))
                    elif conn == '\\':
                        altBranches.update(find_diffUT(con, pres, i, left, right))
                    elif conn == '!':
                        altBranches.update(find_extract(con, pres, i, left, right))
                    elif conn == '^':
                        altBranches.update(find_diffTV(con, pres, i, left, right))
                        altBranches.update(find_diffUT(con, pres, i, right, left))

            if hit_nonatomic:
                return altBranches
            else:
                if len(pres) == 1 and atomicIden(pres[0], con):
                    return {frozenset({tuple(sorted({pres[0], con}))})}
                else:
                    return set()


class DisplaceProof(_LambekProof):
    def parse(self):
        self.proofs = findproof(self.con, *self.pres)


def selfTest():
    from lambekseq.lib.cindex import indexSeq

    con, *pres = 's', '(s^np)!s', '(np\\s)/np', '(s^np)!s'
    (con, *pres), _ = indexSeq(con, pres)
    dsp = DisplaceProof(con, pres)
    dsp.parse()
    dsp.printProofs()


if __name__ == '__main__':
    selfTest()
