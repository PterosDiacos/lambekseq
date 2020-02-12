'''Displacement sequent calculus without products.
This script finds the axioms of every proof.
Write `^` for upward arrow, '!' for downward arrow, '-' for gap.
'''
from cindex import addIndex
from lambek import atomicIden as _atomicIden
from parentheses import bipart as _bipart
from parentheses import isatomic as _isatomic


Gap = '-'


def atomicIden(x, y):
    if Gap in {x, y}:
        return x == y
    else:
        return _atomicIden(x, y)


def bipart(s: str):
    conn, left, right = _bipart(s, 
        connectives={'/', '\\', '^', '!'})
    return conn, left.pop(), right.pop()


def isatomic(s: str):
    return _isatomic(s, connectives={'/', '\\', '^', '!'})


def find_diffTV(con, pres, cut, left, right):
    U = pres[:cut]
    alts = []
    for j in range(cut + 1, len(pres) + 1):
        T, V = pres[cut + 1:j], pres[j:]
        rightproof = findproof(right, *T)
        if rightproof:
            leftproof = findproof(con, *U, left, *V)
            if leftproof:
                alts.append(' [ %s AND %s ] ' % (rightproof, leftproof))
    return alts


def find_diffUT(con, pres, cut, left, right):
    V = pres[cut + 1:]
    alts = []
    for j in range(cut + 1):
        U, T = pres[:j], pres[j:cut]
        leftproof = findproof(left, *T)
        if leftproof:
            rightproof = findproof(con, *U, right, *V)
            if rightproof:
                alts.append(' [ %s AND %s ] ' % (leftproof, rightproof))
    return alts


def find_extract(con, pres, cut, left, right):
    alts = []
    for i in range(cut, -1, -1):
        for j in range(cut, len(pres)):
            if not pres[i:j + 1].count(Gap):
                rightproof = findproof(con, *pres[:i], right, *pres[j + 1:])
                if rightproof:
                    leftproof = findproof(left, *pres[i:cut], Gap, *pres[cut + 1:j + 1])
                    if leftproof:
                        alts.append(' [ %s AND %s ] ' % (leftproof, rightproof))
    return alts


def findproof(con, *pres):
    pres = list(pres)

    # when the conclusion is non-atomic
    if not isatomic(con):
        conn, left, right = bipart(con)
        if conn == '/':
            return findproof(left, *pres, right)        
        elif conn == '\\':
            return findproof(right, left, *pres)
        elif conn == '!':
            return ' [ %s OR %s ] ' % (
                findproof(right, left, *pres),
                findproof(right, *pres, left))
        elif conn == '^':
            try:
                assert pres.count(Gap) <= 1
                cut = pres.index(Gap)
            except AssertionError:
                return ''
            except ValueError:
                alts = []
                for i in range(len(pres) + 1):
                    alts.append(findproof(con, *pres[:i], Gap, *pres[i:]))
                return ' [ %s ] ' % ' OR '.join(filter(None, alts))
            else:
                return findproof(left, *pres[:cut], right, *pres[cut + 1:])
                    
    # when the conclusion is atomic
    else:
        if len(pres) == 0:
            return ''
        else:
            altBranches = []
            hit_nonatomic = False
            for i in range(len(pres)):
                if not isatomic(pres[i]):
                    hit_nonatomic = True
                    conn, left, right = bipart(pres[i])
                    if conn == '/':
                        altBranches.extend(find_diffTV(con, pres, i, left, right))
                    elif conn == '\\':
                        altBranches.extend(find_diffUT(con, pres, i, left, right))
                    elif conn == '!':
                        altBranches.extend(find_extract(con, pres, i, left, right))
                    elif conn == '^':
                        altBranches.extend(find_diffTV(con, pres, i, left, right))
                        altBranches.extend(find_diffUT(con, pres, i, right, left))

            if hit_nonatomic:
                if altBranches:
                    return ' [ %s ] ' % ' OR '.join(altBranches)
                else:
                    return ''
            else:
                if len(pres) == 1 and atomicIden(pres[0], con):
                    return ' [ %s -> %s ] ' % (pres[0], con)
                else:
                    return ''

def indexTokens(con:str, pres:list):
    natom = 0
    alltokens = []
    for s in [con] + pres:
        if s != Gap:
            s, natom = addIndex(s, natom, connectives={'/', '\\', '^', '!'})
        alltokens.append(s)    
    return alltokens


def selfTest():
    from noprodall import parseProof
    con, *pres = 's', '(s^np)!s', '(np\\s)/np', '(s^np)!s'
    con, *pres = indexTokens(con, pres)
    proofs = findproof(con, *pres)
    links = parseProof(proofs)
    print('\n%s <= %s\n' % (con, ' '.join(pres)))
    print(*links, sep='\n', end='\n\n')
    print('Total: %d\n' % len(links))    


if __name__ == '__main__':
    selfTest()
