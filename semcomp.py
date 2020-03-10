import re
import json
from networkx import compose_all

from cindex import indexSeq
from displace import DisplaceProof as Resolver
from atomlink import deAbbr
from semgraph import Semgraph


ABBR_DICT_PATH = '../lambekseq/abbr.json'


def atom2idx(x, pattern=re.compile(r'_(\d+)')):
    return pattern.search(x).group(1)


def xsourceSplit(x, pattern=re.compile(r'g(\d+)x(\d+)')):
    return map(int, pattern.search(x).groups())


def updateQsetbyPair(qset, x, y):
    newEq = {x, y}
    newqset = []
    for S in qset:
        if S & newEq: newEq |= S
        else: newqset.append(S)                
    newqset.append(newEq)
    return newqset    


def quotSet(proof, idxDic, xref, sorts):
    qset = []
    for link in proof:
        x, y = map(atom2idx, link) 
        xtok, ytok = idxDic.toToken[x], idxDic.toToken[y]
        xdep = int(idxDic.toDepth[x]) % sorts[int(xtok) - 1]
        ydep = int(idxDic.toDepth[y]) % sorts[int(ytok) - 1]        
        
        # conclusion is the 0-th token
        if xtok != '0' and ytok != '0':
            qset = updateQsetbyPair(qset, 'g%sa%s' % (xtok, xdep),
                                          'g%sa%s' % (ytok, ydep))

    for x, y in xref:
        qset = updateQsetbyPair(qset, x, y)

    return dict(enumerate(qset))


def unify(con, tokens, xref=[], 
          abbr=json.load(open(ABBR_DICT_PATH))):

    for x, y in xref:
        if 'x' in y: x, y = y, x
        ntok, xsrc = xsourceSplit(x)
        tokens[ntok - 1].add_xsource(xsrc)

    pres = [g.cat for g in tokens]
    sorts = [g.sort for g in tokens]

    for con, pres in deAbbr(con, pres, abbr):
        (con, *pres), idxDic = indexSeq(con, pres)
        parse = Resolver(con, pres)
        parse.parse()

        if parse.proofs:
            _tokens = tokens.copy()
            for i, g in enumerate(_tokens):
                if _tokens[i].cat == 'conj':
                    _tokens[i] = g.conj_expand(idxDic)
                    sorts[i] = _tokens[i].sort

        for p in parse.proofs:
            qset = quotSet(p, idxDic, xref, sorts)
            Gs = []
            
            for g in _tokens:
                relabel = {}
                for v in g.nodes:
                    for i, S in qset.items():
                        if v in S: relabel[v] = 'i%s' % i
                Gs.append(g.iso(relabel))
            
            yield compose_all(Gs)
