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
                                     rruleFirst=True, 
                                     gapLimit=1, **kwargs):

        LambekProof.__init__(self, con, pres, traceMode=traceMode, **kwargs)
        self._gapLimit = gapLimit
        self._islandFirst = islandFirst
        self._rruleFirst = rruleFirst

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


    def find_insert(self, con, pres, cut, left, right):
        '''Deprecated: treating a type as a stack with zero power'''
        leftproof = self.findproof(right)
        if leftproof:
            rightproof = self.findproof(con, *pres[:cut], left, *pres[cut + 1:])
            return {l | r for l in leftproof
                          for r in rightproof}
        return set()


    def find_stack(self, con, base, expo):
        alts = set()
        if not expo: alts.update(self.findproof(con, *base))
        if len(expo) == 1 and not isatomic(expo[0], conn=Conns):
            ec, el, er = bipart(expo[0], conn=Conns, noComma=True)
            if ec == '!':
                leftproof = self.findproof(el, *base)
                if leftproof:
                    rightproof = self.findproof(con, er)
                    alts.update({l | r for l in leftproof
                                       for r in rightproof})
        if len(base) == 1 and not isatomic(base[0], conn=Conns):
            bc, bl, br = bipart(base[0], conn=Conns, noComma=True)
            if bc == '^':
                leftproof = self.findproof(br, *expo)
                if leftproof:
                    rightproof = self.findproof(con, bl)
                    alts.update({l | r for l in leftproof
                                       for r in rightproof})
        return alts


    @usecache
    def _findproof(self, con, *pres):
        pres = list(pres)
        alts = set()
        atomicCon = isatomic(con, conn=Conns)

        # when the conclusion is non-atomic
        if not atomicCon:
            conn, left, right = bipart(con, conn=Conns, noComma=True)
            if conn == '/':
                alts = self.findproof(left, *pres, right)        
            elif conn == '\\':
                alts = self.findproof(right, left, *pres)
            elif conn == '!':
                alts = self.find_stack(right, [left], pres)
            elif conn == '^':
                ngaps = pres.count(Gap)
                if ngaps == 0:
                    for i in range(len(pres) + 1):
                        alts.update(self.findproof(con, *pres[:i], Gap, *pres[i:]))
                    alts.update(self.find_stack(left, pres, [right]))
                elif ngaps <= self._gapLimit:
                    for i in range(len(pres)):
                        if pres[i] == Gap:
                            alts.update(self.findproof(left, *pres[:i], right, *pres[i + 1:]))
            if alts or self._rruleFirst:
                return alts
        
        # when the conclusion is atomic
        if not alts:
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
                    alts.update(self.find_diffTV(con, pres, i, left, right))
                elif conn == '\\':
                    alts.update(self.find_diffUT(con, pres, i, left, right))

            if not (self._islandFirst and nonatomIsland):
                for i, conn, left, right in nonatomPlain:
                    if conn == '/':
                        alts.update(self.find_diffTV(con, pres, i, left, right))
                    elif conn == '\\':
                        alts.update(self.find_diffUT(con, pres, i, left, right))
                    elif conn == '!':
                        alts.update(self.find_extract(con, pres, i, left, right))
                    elif conn == '^':
                        pass

            if nonatomIsland or nonatomPlain:
                return alts
            else:
                if len(pres) == 1 and atomicCon and atomicIden(pres[0], con):
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
