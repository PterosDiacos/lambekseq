'''Product-free Displacement sequent calculus with finite gaps.
This script finds the axioms of every proof.
Write `^` for upward arrow, '!' for downward arrow, '-' for gap.
'''
from lambekseq.lib.cterm import bipart, isatomic, atomicIden, catIden
from lambekseq.lbnoprod import usecache, usetrace
from lambekseq.lbnoprod import LambekProof


Gap = '-'
Conns = {'/', '\\', '^', '!'}
Islands = {'s', 's^np'}


def islandDiv(slash, left, right, islands=Islands):
    if slash == '/':
        return any(catIden(right, i)[0] for i in islands)
    elif slash == '\\':
        return any(catIden(left, i)[0] for i in islands)


class DisplaceProof(LambekProof):
    def __init__(self, con, pres, *, traceMode='trace', 
                                     islandFirst=False, 
                                     gapLimit=1, **kwargs):

        LambekProof.__init__(self, con, pres, traceMode=traceMode, **kwargs)
        self._gapLimit = gapLimit
        self._islandFirst = islandFirst

        DisplaceProof.findproof = usetrace(traceMode)(DisplaceProof._findproof)
        if traceMode == 'trace':
            DisplaceProof.findproof.trace.clear()
        elif traceMode == 'count':
            DisplaceProof.findproof.callCount = 0


    def find_extract(self, con, pres, cut, left, right):
        alts = set()
        for i in range(cut, -1, -1):
            for j in range(cut, len(pres)):
                if pres[i:j + 1].count(Gap) < self._gapLimit:
                    rightproof = self.findproof(con, *pres[:i], right, *pres[j + 1:])
                    if rightproof:
                        leftproof = self.findproof(left, *pres[i:cut], Gap, *pres[cut + 1:j + 1])
                        alts.update({l | r for l in leftproof
                                           for r in rightproof})
        return alts


    def find_double(self, flag, con1, pres1, con2, pres2):
        if flag:
            leftproof = self.findproof(con1, *pres1)
            if leftproof:
                rightproof = self.findproof(con2, *pres2)
                return {l | r for l in leftproof
                              for r in rightproof}
        return set()


    @usecache
    def _findproof(self, con, *pres):
        pres = list(pres)

        # when the conclusion is non-atomic
        if not isatomic(con, conn=Conns):
            conn, left, right = bipart(con, conn=Conns, noComma=True)
            if conn == '/':
                return self.findproof(left, *pres, right)        
            elif conn == '\\':
                return self.findproof(right, left, *pres)
            elif conn == '!':
                alts = set()
                if len(pres) == 1 and not isatomic(pres[0], conn=Conns):
                    pconn, pleft, pright = bipart(pres[0], conn=Conns, noComma=True)
                    alts.update(self.find_double(conn == pconn,
                                                 pleft, [left], right, [pright]))
                if not isatomic(left, conn=Conns):
                    lconn, lleft, lright = bipart(left, conn=Conns, noComma=True)
                    alts.update(self.find_double(lconn == '^',
                                                 lright, pres, right, [lleft]))
                return alts
            elif conn == '^':
                ngaps = pres.count(Gap)
                if ngaps > self._gapLimit:
                    return set()
                elif ngaps == 0:
                    alts = set()
                    for i in range(len(pres) + 1):
                        alts.update(self.findproof(con, *pres[:i], Gap, *pres[i:]))
                    if len(pres) == 1 and not isatomic(pres[0], conn=Conns):
                        pconn, pleft, pright = bipart(pres[0], conn=Conns, noComma=True)
                        alts.update(self.find_double(conn == pconn, 
                                                     left, [pleft], pright, [right]))
                    if not isatomic(right, conn=Conns):
                        rconn, rleft, rright = bipart(right, conn=Conns, noComma=True)
                        alts.update(self.find_double(rconn == '!',
                                                     rleft, pres, left, [rright]))
                    return alts
                else:
                    alts = set()
                    for i in range(len(pres)):
                        if pres[i] == Gap:
                            alts.update(self.findproof(left, *pres[:i], right, *pres[i + 1:]))
                    return alts

        # when the conclusion is atomic
        else:
            altBranches = set()
            nonatomPlain = []
            nonatomIsland = []
            for i in range(len(pres)):
                if not isatomic(pres[i], conn=Conns):
                    conn, left, right = bipart(pres[i], conn=Conns, noComma=True)
                    if islandDiv(conn, left, right):
                        nonatomIsland.append((i, conn, left, right))
                    else:
                        nonatomPlain.append((i, conn, left, right))

            for i, conn, left, right in nonatomIsland:
                if conn == '/':
                    altBranches.update(self.find_diffTV(con, pres, i, left, right))
                elif conn == '\\':
                    altBranches.update(self.find_diffUT(con, pres, i, left, right))

            if not self._islandFirst or not nonatomIsland:
                for i, conn, left, right in nonatomPlain:
                    if conn == '/':
                        altBranches.update(self.find_diffTV(con, pres, i, left, right))
                    elif conn == '\\':
                        altBranches.update(self.find_diffUT(con, pres, i, left, right))
                    elif conn == '!':
                        altBranches.update(self.find_extract(con, pres, i, left, right))
                    elif conn == '^':
                        pass

            if nonatomIsland or nonatomPlain:
                return altBranches
            else:
                if len(pres) == 1 and atomicIden(pres[0], con):
                    return {frozenset({tuple(sorted({pres[0], con}))})}
                else:
                    return set()


def selfTest():
    from lambekseq.lib.cindex import indexSeq

    con, *pres = 's', '(s^np)!s', '(np\\s)/np', '(s^np)!s'
    (con, *pres), _ = indexSeq(con, pres)
    dsp = DisplaceProof(con, pres)
    dsp.parse()
    dsp.buildTree()
    dsp.printTree()


if __name__ == '__main__':
    selfTest()
