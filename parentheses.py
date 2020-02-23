'''Utilities for handling category terms.
'''
import re


def isatomic(s: str, conn={'/', '\\'}):
    '''Check if `s` contains connectives.'''
    return not any(c in s for c in conn)


def commaSplit(s: str):
    '''Split `s` at its top-level commas.'''
    count = 0
    for i in range(len(s)):
        if s[i] == '(': count += 1
        elif s[i] == ')': count -= 1
        elif s[i] == ',':
            if count == 0: return [s[:i]] + commaSplit(s[i + 1:])
    else:
        return [s]


def stripparentheses(s: str, leftPr='(', rightPr=')'):
    '''Remove redundant parentheses in `s`.'''
    s = s.strip()
    count = 0
    if s.startswith(leftPr):
        for i in range(len(s)):
            if s[i] == leftPr: count += 1
            elif s[i] == rightPr:
                count -= 1
                if count == 0 and i < len(s) -1: return s
        else:
            return stripparentheses(s[1:-1], leftPr, rightPr)
    else:
        return s


def bipart(s: str, leftPr='(', rightPr=')',
           conn={'/', '\\'}, noComma=False,
           connMod={'$'}, withMod=False):
    '''Break a non-atomic `s` into slashes, the left and right components. 
    Both components are lists of strings if `noComma` is `False`.
    Slashes can be followed by a modal specifier in `connMod`.
    Return the modal specifier if `withMod` is `True`.'''
    s = stripparentheses(s)
    count = 0

    for i in range(len(s)):
        if s[i] == leftPr:
            count += 1
        elif s[i] == rightPr:
            count -= 1
        elif count == 0 and s[i] in conn:
            if s[i + 1] in connMod:
                smod = s[i + 1]
                j = 2
            else:
                smod = ''
                j = 1

            left, right = stripparentheses(s[:i]), stripparentheses(s[i + j:]) 
            left, right = commaSplit(left), commaSplit(right)
            if noComma: left, right = left.pop(), right.pop()
            
            if withMod:
                return s[i], smod, left, right
            else:
                return s[i], left, right


def addHypo(x, slash, hypo, fwd={'/', '^'}, 
                            bkd={'\\', '!'}):   
    if slash is None: return x

    x = x if isatomic(x, fwd | bkd) else '(%s)' % x
    hypo = hypo if isatomic(hypo, fwd | bkd) else '(%s)' % hypo

    if slash in fwd:
        return '%s%s%s' % (x, slash, hypo)
    elif slash in bkd:
        return '%s%s%s' % (hypo, slash, x)


def unslash(x:str, conn={'/', '\\', '^', '!'}) -> [('root', 'slash', 'div')]:
    '''No commas in `x`. Recognize only `/` and `\\`.'''
    xlist = [(x, None, None)]

    while not isatomic(xlist[-1][0], conn=conn):
        xslash, xleft, xright = bipart(xlist[-1][0], conn=conn, noComma=True)
        if xslash == '/':
            xlist.append((xleft, '/', xright))
        elif xslash == '\\':
            xlist.append((xright, '\\', xleft))
        else:
            break

    return xlist


def catIden(x:str, y:str, conn={'/', '\\', '^', '!'}) -> (bool, frozenset):
    '''No commas in `x` and `y`.'''
    atomCount = int(isatomic(x, conn=conn)) + int(isatomic(y, conn=conn))    
    if atomCount == 2:
        return atomicIden(x, y), frozenset({tuple(sorted({x, y}))}) 
         
    elif atomCount == 0:
        xslash, xleft, xright = bipart(x, conn=conn, noComma=True)
        yslash, yleft, yright = bipart(y, conn=conn, noComma=True)
        
        if xslash == yslash:
            leftIden, leftPairs = catIden(xleft, yleft)
            rightIden, rightPairs = catIden(xright, yright)
            return leftIden and rightIden, leftPairs | rightPairs

    return False, frozenset()


def atomicIden(x: str, y: str, 
               pattern=re.compile(r'(?:\A|\()(?:\W*)([a-zA-Z]+)_?(\d*)(?:\Z|\))'), 
               indexIden=False):
    '''Check if `x` equals `y` (up to indexation).'''
    x, x_i = pattern.search(x).groups()
    y, y_i = pattern.search(y).groups()
    return x == y and (not indexIden or x_i == y_i)
