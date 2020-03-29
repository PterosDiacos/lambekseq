import json
import argparse

from lambekseq.lbnoprod import LambekProof
from lambekseq.displace import DisplaceProof
from lambekseq.cmll import ProofNet
from lambekseq.cntccg import Cntccg

from lambekseq.lib.cindex import indexSeq
from lambekseq.lib.cterm import bipart, isatomic


CALC_DICT = dict(ccg=Cntccg,
                 dsp=DisplaceProof,
                 lb=LambekProof,
                 pn=ProofNet)


def deAbbr(con: str, pres: list, abbr: dict, 
           calc=DisplaceProof,
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

    def slashOnly(con, pres):
        f = lambda x: '^' in x or '!' in x
        return not any(f(x) for x in [con, *pres])

    for con, *pres in gen([con] + pres):
        if calc in {DisplaceProof, Cntccg}:
            yield con, pres
        elif slashOnly(con, pres):
            yield con, pres


def searchLinks(cls, con, pres, **kwargs):
    '''Return the indexed `con`, `pres`,
    the run parser and the index dictionary `idxDic`.
    `idxDic.toToken` maps indices to token numbers.
    `idxDic.toDepth` maps indices to atom depths.
    '''
    (con, *pres), idxDic = indexSeq(con, pres)   
    if cls == ProofNet:
        parser = cls.fromLambekSeq(con, pres, **kwargs)
    else:
        parser = cls(con, pres, **kwargs)
    
    parser.parse()
    return con, pres, parser, idxDic


def printLinks(con, pres, parser):
    if parser.proofCount:
        print('%s\n%s <= %s\n' % ('-' * 10, con, ' '.join(pres)))
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
    ap.add_argument('--offSymbolOnly',
        default=False,
        action='store_true',
        help='[default] False. Used by Proofnet.'
    )
    ap.add_argument('--offEarlyCollapse',
        default=False,
        action='store_true',
        help='[default] False. Used by continuized CCG.'
    )
    ap.add_argument('--offMatchConn',
        default=False,
        action='store_true',
        help='[default] False. Used by continuized CCG.'
    )
    ap.add_argument('--concatFirst',
        default=False,
        action='store_true',
        help='[default] False. Used by Displacement calculus.'
    )
    return ap


if __name__ == '__main__':
    args = initArgParser().parse_args()

    con, *pres = json.load(open(args.json))[0]
    abbr = json.load(open(args.abbr))
    calc = CALC_DICT.get(args.calc, DisplaceProof)
    print(calc)

    total = 0
    for con, pres in deAbbr(con, pres, abbr, calc):
        con, pres, parser, _ = searchLinks(calc, con, pres, 
                                           symbolOnly=not args.offSymbolOnly,
                                           earlyCollapse=not args.offEarlyCollapse,
                                           matchConn=not args.offMatchConn,
                                           concatFirst=args.concatFirst)
        total += parser.proofCount
        printLinks(con, pres, parser)

    if not total: print('Total: 0\n')
