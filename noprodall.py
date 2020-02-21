'''Lambek sequent calculus without products in conclusion. 
This script finds the axioms of every proof.
'''
from itertools import product
from functools import reduce
from operator import concat
from parentheses import stripparentheses, isatomic, bipart
from lambek import atomicIden


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


def findproof(con, *pres):
    '''Find proofs by showing the axiomatic premises.'''
    # when the conclusion is non-atomic
    if not isatomic(con):
        slash, left, right = bipart(con, noComma=True)
        if slash == '/':
            return findproof(left, *pres, right)
        elif slash == '\\':
            return findproof(right, left, *pres)

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
                    slash, left, right = bipart(pres[i], noComma=True)
                    if slash == '/':
                        altBranches.extend(find_diffTV(con, pres, i, left, right))
                    elif slash == '\\':
                        altBranches.extend(find_diffUT(con, pres, i, left, right))

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


def getConn(s):
    if 'OR' in s or 'AND' in s:
        count = 0
        for i in range(len(s)):
            if s[i] == '[': count +=1
            elif s[i] == ']': count -= 1
            elif count == 0:
                if s[i: i + 2] == 'OR': return 'OR'
                elif s[i: i + 3] == 'AND': return 'AND'
    else:
        return None


def getTerms(s, conn):
    terms = []
    count = 0
    for i in range(len(s)):
        if s[i] == '[':
            count += 1
            if count == 1: lastOpen = i
        elif s[i] == ']':
            count -= 1
            if  count == 0 and conn not in s[i:]: 
                terms.append(s[lastOpen:i + 1])
        elif count == 0 and s[i:i + len(conn)] == conn:
            terms.append(s[lastOpen:i])
    return terms


def makeTree(s):
    s = stripparentheses(s, leftPr='[', rightPr=']')
    conn = getConn(s)
    if not conn:
        return stripparentheses(s, leftPr='[', rightPr=']')
    else:
        return (conn, [makeTree(t) for t in getTerms(s, conn)])


def tree2links(tree):
    if isinstance(tree, str):
        return {(tree,)}
    else:
        if tree[0] == 'AND':
            return {reduce(concat, x) for x in 
                set(product(*(tree2links(b) for b in tree[1])))}
        elif tree[0] == 'OR':
            return set.union(*(tree2links(b) for b in tree[1]))


def parseProof(s):
    tree = makeTree(s)
    if tree:
        links = {frozenset(l) for l in tree2links(tree)}
        return {tuple(sorted(l)) for l in links}
    else:
        return set()
