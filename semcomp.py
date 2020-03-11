'''Semantic composition module.
Composing semgraphs based on atom links given by CG calculus and co-referencing
and indefinite scoping.
'''
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
    '''Find the quotient set of nodes based on atom links and 
    co-referencing and scoping. Atom-node correspondence is given
    by atom depths.'''
    qset = []
    for link in proof:
        x, y = map(atom2idx, link) 
        xtok, ytok = idxDic.toToken[x], idxDic.toToken[y]
        xdep = int(idxDic.toDepth[x]) % sorts[int(xtok) - 1]
        ydep = int(idxDic.toDepth[y]) % sorts[int(ytok) - 1]        
        
        # conclusion is the 0-th token
        if xtok != '0' and ytok != '0':
            # distinct nodes of the same token are not to be fused
            if xtok == ytok and xdep != ydep: return dict()

            qset = updateQsetbyPair(qset, 'g%sa%s' % (xtok, xdep),
                                          'g%sa%s' % (ytok, ydep))

    for x, y in xref:
        qset = updateQsetbyPair(qset, x, y)

    return dict(enumerate(qset))


class PackSyntax:
    __slots__ = ['con', 'pres', 'links', 'idxDic', '__str']
    def __init__(self, con, pres, links, idxDic):
        self.con = con
        self.pres = pres
        self.idxDic = idxDic
        self.links = links
        self.__str = ', '.join(sorted('(%s, %s)' % (i, j) 
                                        for (i, j) in links))


class SemComp:
    '''`tokens`: a list of (WORD, POS) pairs.
    POS is the key to lexical schemes in vocabulary. The constructor 
    converts this list ino a list of semgraphs.

    `xref`: a list of (SOURCE1, SOURCE2) manually encoded atom links 
    given by co-referencing and indefinite-scoping.
    SOURCE1 is of the form `gixj`, the j-th x-prefixed source of the 
    i-th token; SOURCE2 is of the form `gka0`, the 0-th a-prefixed
    source of the k-th token. In case of co-referencing, SOURCE2 is 
    the antecedent of SOURCE1. In caes of scoping, SOURCE2 is the node 
    before which SOURCE1 should be valued. 

    `calc`: the CG calculus used to find atom links.

    `abbr`: a dictionary that defines abbreviated syntactic categories.
    See `atomlink` module.

    `vocab`: a dictionary of lexical schemes. 
    '''
    def __init__(self, tokens, xref=[], calc='dsp',
                 abbr=json.load(open(ABBR_DICT_PATH)),
                 vocab=json.load(open(VOCAB_SCHEMA_PATH))):
        self.tokens = [Semgraph.from_dict(vocab[pos], lex, i + 1)
                       for i, (lex, pos) in enumerate(tokens)]
        self.xref = xref
        self.calc = al.CALC_DICT.get(calc, al.DisplaceProof)
        self.abbr = abbr
    

    def unify(self, con:str='s'):
        self.semantics = []
        self.syntax = []

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
                
                self.semantics.append(compose_all(Gs))
                self.syntax.append(PackSyntax(
                    con=con, pres=pres, links=p, idxDic=idxDic))
