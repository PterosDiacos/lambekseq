from cindex import indexToken, idx2depthDict, depthtag
from cmll import ProofNet
from noprodall import findproof, parseProof


def pnLinks(con: str, pres: list):
    (con, *pres), _ = indexToken(con, pres)
    pn = ProofNet.fromLambekSeq(con, pres)
    pn.buildProofs()
    if pn.proofCount:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        pn.printProofLinks()
        print('Total: %d\n' % pn.proofCount)


def noprodLinks(con, pres):
    (con, *pres), _ = indexToken(con, pres)
    proofs = findproof(con, *pres)
    links = parseProof(proofs)
    if links:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        print(*links, sep='\n')
        print('Total: %d\n' % len(links))


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
    abbr = {
        'vpPrep': ['((np\\s)\\(np\\s))/np', '(s\\s)/np'],
        'qnt': ['(s/(np\\s))/n', '((s/np)\\s)/n'],
        'vt': ['(np\\s)/np']
    }
    con, *pres = 's', 'qnt', 'n', 'vt', 'qnt', 'n', 'vpPrep', 'qnt', 'n'
    
    for con, pres in deAbbr(con, pres, abbr):
        pnLinks(con, pres)
        # noprodLinks(con, pres)
