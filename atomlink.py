import json
import argparse

from lbnoprod import LambekProof
from displace import DisplaceProof
from cmll import ProofNet
from cntccg import Cntccg

from lib.cindex import indexSeq
from lib.parentheses import bipart, isatomic


CALC_DICT = dict(ccg=Cntccg,
                 dsp=DisplaceProof,
                 lb=LambekProof,
                 pn=ProofNet)


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


def searchLinks(cls, con, pres):
    '''Return the indexed `con`, `pres`,
    the run parser and the index dictionary `idxDic`.
    `idxDic.toToken` maps indices to token numbers.
    `idxDic.toDepth` maps indices to atom depths.
    '''
    (con, *pres), idxDic = indexSeq(con, pres)   
    if cls == ProofNet:
        parser = cls.fromLambekSeq(con, pres)
    else:
        parser = cls(con, pres)
    
    parser.parse()
    return con, pres, parser, idxDic


def printLinks(con, pres, parser):
    if parser.proofCount:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
        if isinstance(parser, ProofNet):
            parser.printProofs(symbolOnly=True)
        else:
            parser.printProofs()      
        print('Total: %d\n' % parser.proofCount)


def initArgParser():
    ap = argparse.ArgumentParser(
        description='CG based Atom Linker')
    ap.add_argument('-j', '--json', 
        default='input.json',
        help='[default] "input.json". '
             'A json file that contains a list of lists, '
             'the first of which serves as the input '
             'sequent.')
    ap.add_argument('-a', '--abbr',
        default='abbr.json',
        help='[default] "abbr.json". '
             'A json file that contains a dictionary, '
             'whose keys are abbreviated categories, '
             'whose values are lists of actual '
             'categories.'
    )
    ap.add_argument('-c', '--calc',
        default='dsp',
        help='[default] "dsp". '
             'The calculus used to resolve atom links. '
             'ccg for continuized CCG; '
             'dsp for Displacement calculus; '
             'lb for classic Lambek calculus; '
             'pn for Proofnet based Lambek calculus.'
    )
    return ap


if __name__ == '__main__':
    args = initArgParser().parse_args()

    con, *pres = json.load(open(args.json))[0]
    abbr = json.load(open(args.abbr))
    f = CALC_DICT.get(args.calc, DisplaceProof)
    print(f)

    total = 0
    for con, pres in deAbbr(con, pres, abbr):
        con, pres, parser, _ = searchLinks(f, con, pres)
        total += parser.proofCount
        printLinks(con, pres, parser)

    if not total: print('Total: 0\n')
