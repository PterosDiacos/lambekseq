import re
import pprint as pp
from parentheses import isatomic, bipart


def corder(s: str):
    '''Category order per (Pentus, 2010).'''
    if isatomic(s):
        return 0
    else:
        slash, left, right = bipart(s)
        if slash == '/':
            maxRight = max(corder(r) for r in right) + 1
            maxLeft = (max(corder(l) for l in left) 
                       + 2 * (min(len(left), 2) - 1))
        else:
            maxLeft = max(corder(l) for l in left) + 1
            maxRight = (max(corder(r) for r in right) 
                        + 2 * (min(len(right), 2) - 1))
        return max(maxLeft, maxRight)


def divOrdTag(s: str, divOrder=0):
    '''Tag each atomic symbol with the order of its divisor.'''
    if isatomic(s):
        return ('%s#%d' % (s, divOrder), )
    else:
        slash, left, right = bipart(s)
        taggedleft = taggedright = ()
        if slash == '/':
            rightOrder = (max(corder(r) for r in right)
                          + 2 * (min(len(right), 2) - 1))
            for l in left:
                taggedleft += divOrdTag(l, rightOrder)
            for r in right:
                taggedright += divOrdTag(r)
        else:
            leftOrder = (max(corder(l) for l in left)
                         + 2 * (min(len(left), 2) - 1))
            for r in right:
                taggedright += divOrdTag(r, leftOrder)
            for l in left:
                taggedleft += divOrdTag(l)
        return (*taggedleft, slash, *taggedright)


def depthTag(s: str, rootdepth=0, chopcount=0):
    '''Tag each atomic symbol with its depth. No top level comma.'''
    if isatomic(s):
        return ('%s:%d' % (s, rootdepth), )
    else:
        slash, left, right = bipart(s)
        taggedleft = taggedright = ()
        if slash == '/':
            for r in right:
                taggedright += depthTag(r, rootdepth + chopcount + 1, 0)
            for l in left:
                taggedleft += depthTag(l, rootdepth, chopcount + 1)
        else:
            for l in left:
                taggedleft += depthTag(l, rootdepth + chopcount + 1, 0)
            for r in right:
                taggedright += depthTag(r, rootdepth, chopcount + 1)
        return (*taggedleft, slash, *taggedright)


def idx2depthDict(tagged, pattern=re.compile(r'_(\d+):(\d+)')):
    return dict({pattern.search(x).groups() 
        for x in tagged if x not in {'/', '\\'}})


def idx2ordDict(tagged, pattern=re.compile(r'_(\d+)#(\d+)')):
    return idx2depthDict(tagged, pattern=pattern)


def addIndex(s, natom, conn={'/', '\\'}):
    if isatomic(s, conn=conn):
        return '%s_%d' % (s, natom), natom + 1

    else:
        slash, left, right = bipart(s, conn=conn)      

        sleft = []
        for l in left:
            s, natomL = addIndex(l, natom, conn=conn)
            sleft.append(s)
            natom = natomL
        sleft = ','.join(sleft)

        sright = []
        for r in right:
            s, natomR = addIndex(r, natom, conn=conn)
            sright.append(s)
            natom = natomR
        sright = ','.join(sright)
        
        if not isatomic(sleft, conn=conn | {','}): sleft = '(%s)' % sleft
        if not isatomic(sright, conn=conn | {','}): sright = '(%s)' % sright

        return sleft + slash + sright, natom


def indexSeq(con: str, pres: list):
    '''Return tokens in `con` + `pres` with indices added to atoms.
    Return also three maps from atom indices:
     - to the token number;
     - to the atom's depth;
     - to the atom's divisor order.
    '''
    natom = 0
    alltokens = []
    idx2Token = {}
    idx2Depth = {}
    idx2Order = {}

    for n, s in enumerate([con] + pres):
        s, natom1 = addIndex(s, natom)
        alltokens.append(s)

        for idx in range(natom, natom1): 
            idx2Token[str(idx)] = str(n)
        idx2Depth.update(idx2depthDict(depthTag(s)))
        idx2Order.update(idx2ordDict(divOrdTag(s)))

        natom = natom1

    class FromIndex:
        toToken = idx2Token
        toDepth = idx2Depth
        toOrder = idx2Order
        def __str__(self):
            return pp.pformat(dict(toToken=self.toToken,
                                   toDepth=self.toDepth,
                                   toOrder=self.toOrder))

    return alltokens, FromIndex()
