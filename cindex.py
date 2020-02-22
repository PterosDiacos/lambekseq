import re
import pprint as pp
from parentheses import isatomic, bipart


StopAtoms = {'-'}
Conns = {'/', '\\', '^', '!'}
Modifiers = {'$'}


def depthTag(s: str, rootdepth=0, chopcount=0,
             fdConn={'/', '^'}, bkConn={'\\', '!'}):
    '''Tag each atomic symbol with its depth. No top level comma.'''
    if isatomic(s, conn=Conns):
        return ('%s:%d' % (s, rootdepth), )
    else:
        slash, smod, left, right = bipart(s, 
            conn=Conns, connMod=Modifiers, withMod=True)
        taggedleft = taggedright = ()

        if not smod:
            if slash in fdConn:
                for l in left:
                    taggedleft += depthTag(l, rootdepth, chopcount + 1)
                for r in right:
                    taggedright += depthTag(r, rootdepth + chopcount + 1, 0)
            elif slash in bkConn:
                for r in right:
                    taggedright += depthTag(r, rootdepth, chopcount + 1)
                for l in left:
                    taggedleft += depthTag(l, rootdepth + chopcount + 1, 0)
        
        elif smod in Modifiers:
            for l in left:
                taggedleft += depthTag(l, rootdepth, chopcount)
            for r in right:
                taggedright += depthTag(r, rootdepth, chopcount)
        
        return (*taggedleft, slash, *taggedright)


def idx2depthDict(tagged, conn=Conns,
                  pattern=re.compile(r'_(\d+):(\d+)')):    
    return dict({pattern.search(x).groups() 
        for x in tagged if x not in conn})


def addIndex(s, natom, conn=Conns):
    '''Number atomic symbols from left to right. No top level comma.'''
    if isatomic(s, conn=conn):
        if s in StopAtoms:
            return s, natom
        else:
            return '%s_%d' % (s, natom), natom + 1

    else:
        slash, smod, left, right = bipart(s, 
            conn=conn, connMod=Modifiers, withMod=True)      

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

        return sleft + slash + smod + sright, natom


def indexSeq(con: str, pres: list):
    '''Return tokens in `con` + `pres` with indices added to atoms.
    Return also two maps from atom indices:
     - to the token number;
     - to the atom's depth.
    '''
    natom = 0
    stopCount = 0
    alltokens = []
    idx2Token = {}
    idx2Depth = {}

    for n, s in enumerate([con] + pres):
        s, natom1 = addIndex(s, natom)
        alltokens.append(s)

        for idx in range(natom, natom1): 
            idx2Token[str(idx)] = str(n - stopCount)

        if s in StopAtoms:
            stopCount += 1
        else:
            idx2Depth.update(idx2depthDict(depthTag(s)))

        natom = natom1

    class FromIndex:
        toToken = idx2Token
        toDepth = idx2Depth
        def __str__(self):
            return pp.pformat(dict(toToken=self.toToken,
                                   toDepth=self.toDepth))

    return alltokens, FromIndex()
