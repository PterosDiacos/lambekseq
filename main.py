import json
import sys
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
    elif cls == Cntccg:
        agent = cls(pres)
    else:
        agent = cls(con, pres)

    agent.parse()
    
    if agent.proofCount:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        if cls == ProofNet:
            agent.printProofs(symbolOnly=True)
        elif cls == Cntccg:
            agent.printProofs(con)
        else:
            agent.printProofs()      
        print('Total: %d\n' % agent.proofCount)
    
    return agent.proofCount


def deAbbr(con: str, pres: list, abbr: dict):
    def gen(L):
        if L:
            head, *tail = L
            for hopt in abbr.get(head, [head]):
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
