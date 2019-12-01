import re
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


def depthtag(s: str, rootdepth=0, chopcount=0):
    '''Tag each atomic symbol with its depth. No top level comma.'''
    if isatomic(s):
        return ('%s:%d' % (s, rootdepth + chopcount), )
    else:
        slash, left, right = bipart(s)
        taggedleft = taggedright = ()
        if slash == '/':
            for r in right:
                taggedright += depthtag(r, rootdepth + chopcount + 1, 0)
            for l in left:
                taggedleft += depthtag(l, rootdepth, 0) if isatomic(l) \
                                                        else depthtag(l, rootdepth, chopcount + 1)
        else:
            for l in left:
                taggedleft += depthtag(l, rootdepth + chopcount + 1, 0)
            for r in right:
                taggedright += depthtag(r, rootdepth, 0) if isatomic(r) \
                                                         else depthtag(r, rootdepth, chopcount + 1)
        return (*taggedleft, slash, *taggedright)


def idx2depthDict(tagged, pattern=re.compile(r'_(\d+):(\d+)')):
    return dict({pattern.search(x).groups() 
        for x in tagged if x not in {'/', '\\'}})


def idx2ordDict(tagged, pattern=re.compile(r'_(\d+)#(\d+)')):
    return idx2depthDict(tagged, pattern=pattern)


def addIndex(s, natom):
    if isatomic(s):
        return '%s_%d' % (s, natom), natom + 1
    else:
        slash, left, right = bipart(s)
        left, right = left.pop(), right.pop()
        sleft, natomLeft = addIndex(left, natom)
        sright, natomRight = addIndex(right, natomLeft)

        if not isatomic(sleft): sleft = '(%s)' % sleft
        if not isatomic(sright): sright = '(%s)' % sright        
        return sleft + slash + sright, natomRight


def indexToken(con: str, pres: list):
    '''Return tokens in `con` + `pres` with indices added to atoms.
    Return also a dictionary that maps an atom index to the token number.'''
    natom = 0
    alltokens = []
    idx2TokenNum = {}

    for n, s in enumerate([con] + pres):
        s, natom1 = addIndex(s, natom)
        alltokens.append(s)
        for idx in range(natom, natom1): idx2TokenNum[idx] = n
        natom = natom1        
    return alltokens, idx2TokenNum
