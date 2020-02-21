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


def addHypo(x, slash, hypo):
    if slash is None:
        return x

    x = x if isatomic(x) else '(%s)' % x
    hypo = hypo if isatomic(hypo) else '(%s)' % hypo

    if slash == '/':
        return '%s/%s' % (x, hypo)
    else:
        return '%s\\%s' % (hypo, x)


def unslash(x:str):
    '''No commas in `x`.'''
    xlist = [(x, None, None)]

    while not isatomic(xlist[-1][0]):
        xslash, xleft, xright = bipart(xlist[-1][0], noComma=True)
        if xslash == '/':
            xlist.append((xleft, '/', xright))
        else:
            xlist.append((xright, '\\', xleft))

    return xlist


def catIden(x:str, y:str) -> (bool, set):
    '''No commas in `x` and `y`.'''
    atomCount = int(isatomic(x)) + int(isatomic(y))    
    if atomCount == 2:
        return atomicIden(x, y), {tuple(sorted({x, y}))}
         
    elif atomCount == 0:
        xslash, xleft, xright = bipart(x, noComma=True)
        yslash, yleft, yright = bipart(y, noComma=True)
        
        if xslash == yslash:
            leftIden, leftPairs = catIden(xleft, yleft)
            rightIden, rightPairs = catIden(xright, yright)
            return leftIden and rightIden, leftPairs | rightPairs

    return False, set()


def atomicIden(x: str, y: str, 
               pattern=re.compile(r'(?:\A|\()(?:\W*)([a-zA-Z]+)_?(\d*)(?:\Z|\))'), 
               indexIden=False):
    '''Check if `x` equals `y` (up to indexation).'''
    x, x_i = pattern.search(x).groups()
    y, y_i = pattern.search(y).groups()
    return x == y and (not indexIden or x_i == y_i)
