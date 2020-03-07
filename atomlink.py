import json
import sys
from parentheses import bipart, isatomic
from cindex import indexSeq
from lbnoprod import LambekProof
from displace import DisplaceProof
from cmll import ProofNet
from cntccg import Cntccg


PaserDict = {0: ProofNet,
             1: LambekProof,
             2: Cntccg,
             3: DisplaceProof}


def searchLinks(cls, con, pres):
    (con, *pres), _ = indexSeq(con, pres)   
    if cls == ProofNet:
        agent = cls.fromLambekSeq(con, pres)
    else:
        agent = cls(con, pres)

    agent.parse()
    
    if agent.proofCount:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        if cls == ProofNet:
            agent.printProofs(symbolOnly=True)
        else:
            agent.printProofs()      
        print('Total: %d\n' % agent.proofCount)
    
    return agent.proofCount


def deAbbr(con: str, pres: list, abbr: dict, 
           conn={'/', '\\', '^', '!'}):    
    def zoomin(s):
        if isatomic(s, conn=conn):
            for opt in abbr.get(s, [s]):
                if opt == s:
                    yield opt
                else:
                    for opt1 in zoomin(opt):
                        yield opt1
        else:
            slash, smod, l, r = bipart(s,
                conn=conn, noComma=True, withMod=True)
            for lopt in zoomin(l):
                for ropt in zoomin(r):
                    if not isatomic(lopt, conn=conn):
                        lopt = '(%s)' % lopt
                    if not isatomic(ropt, conn=conn):
                        ropt = '(%s)' % ropt
                    yield lopt + slash + smod + ropt
    def gen(L):
        if L:
            head, *tail = L
            for hopt in zoomin(head):
                for topt in gen(tail): 
                    yield [hopt] + topt
        else:
            yield []
    for con, *pres in gen([con] + pres):
        yield con, pres


if __name__ == '__main__':
    con, *pres = json.load(open('input.json'))[0]
    abbr = json.load(open('abbr.json'))

    # defaults to Cntccg
    f = PaserDict[int(sys.argv[1])] if len(sys.argv) > 1 \
                                    else Cntccg
    print(f)

    total = 0
    for con, pres in deAbbr(con, pres, abbr):
        total += searchLinks(f, con, pres)

    if not total: print('Total: 0\n')
