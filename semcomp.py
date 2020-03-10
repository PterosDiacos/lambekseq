import re
import json
from networkx import compose_all

import atomlink as al
from semgraph import Semgraph


VOCAB_SCHEMA_PATH = '../lambekseq/schema.json'
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


class SemComp:
    def __init__(self, tokens, xref=[], calc='dsp',
                 abbr=json.load(open(ABBR_DICT_PATH)),
                 vocab=json.load(open(VOCAB_SCHEMA_PATH))):
        self.tokens = [Semgraph.from_dict(vocab[pos], lex, i + 1)
                       for i, (lex, pos) in enumerate(tokens)]
        self.xref = xref
        self.calc = al.CALC_DICT.get(calc, al.DisplaceProof)
        self.abbr = abbr
    

    def unify(self, con:str='s'):
        self.result = []

        for x, y in self.xref:
            if 'x' in y: x, y = y, x
            ntok, xsrc = xsourceSplit(x)
            self.tokens[ntok - 1].add_xsource(xsrc)

        pres = [g.cat for g in self.tokens]
        sorts = [g.sort for g in self.tokens]

        for con, pres in al.deAbbr(con, pres, self.abbr):
            con, pres, parse, idxDic = al.searchLinks(self.calc, con, pres)

            if parse.proofs:
                _tokens = self.tokens.copy()
                for i, g in enumerate(_tokens):
                    if _tokens[i].cat == 'conj':
                        _tokens[i] = g.conj_expand(idxDic)
                        sorts[i] = _tokens[i].sort

            for p in parse.proofs:
                qset = quotSet(p, idxDic, self.xref, sorts)
                Gs = []
                for g in _tokens:
                    relabel = {}
                    for v in g.nodes:
                        for i, S in qset.items():
                            if v in S: relabel[v] = 'i%s' % i
                    Gs.append(g.iso(relabel))
                
                self.result.append(compose_all(Gs))
