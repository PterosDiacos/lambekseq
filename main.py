from cindex import indexToken, idx2depthDict, depthtag
from cmll import ProofNet
from noprodall import findproof, parseProof


def pnLinks(con: str, pres: list):
    (con, *pres), _ = indexToken(con, pres)
    pn = ProofNet.fromLambekSeq(con, pres)
    pn.buildProofs()
    if pn.proofCount:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        pn.printProofLinks(symbolOnly=True)
        print('Total: %d\n' % pn.proofCount)
    
    return pn.proofCount


def noprodLinks(con, pres):
    (con, *pres), _ = indexToken(con, pres)
    proofs = findproof(con, *pres)
    links = parseProof(proofs)
    if links:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        print(*links, sep='\n', end='\n\n')
        print('Total: %d\n' % len(links))
    
    return len(links)


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
    from exam import con, pres
    abbr = {
        'qt':     ['(s/(np\\s))/n', '((s/np)\\s)/n'],
        'qnp':    ['s/(np\\s)', '(s/np)\\s'],
        'vt':     ['(np\\s)/np'],
        'vp':     ['np\\s'],
        'inv':    ['((np\\s)\\(np\\s))/np', '(s\\s)/np'],
        'inn':    ['(n\\n)/np'],
        'rl':     ['(n\\n)/(s/np)', '(n\\n)/(np\\s)'],
    }

    pnLinks.count = 0
    noprodLinks.count = 0

    for con, pres in deAbbr(con, pres, abbr):
        pnLinks.count += pnLinks(con, pres)
        # noprodLinks.count += noprodLinks(con, pres)

    if not (pnLinks.count or noprodLinks.count):
        print('Total : 0\n')
