'''Lambek sequent calculus with products in conclusion.
This script finds one proof with all inferential steps.
'''
import re
import sys
from parentheses import bipart, isatomic


def idxpair2set(x_i, y_i):
    if x_i and y_i:
        return {tuple(sorted({x_i, y_i}))}
    else:
        return set()


def catIden(x:str, y:str, 
    pattern=re.compile(r'([a-zA-Z]+)_?(\d*)')
    ) -> (bool, set):    
    if isatomic(x) and isatomic(y):
        x, x_i = pattern.search(x).groups()
        y, y_i = pattern.search(y).groups()
        return x == y, idxpair2set(x_i, y_i)
    
    if not isatomic(x) and not isatomic(y):
        xslash, xleft, xright = bipart(x)
        xleft, xright = xleft[0], xright[0]
        yslash, yleft, yright = bipart(y)
        yleft, yright = yleft[0], yright[0]
        
        if xslash == yslash:
            leftIden, leftPairs = catIden(xleft, yleft)
            rightIden, rightPairs = catIden(xright, yright)
            return leftIden and rightIden, leftPairs | rightPairs

    return False, set()


def atomicIden(x: str, y: str, pattern=re.compile(r'([a-zA-Z]+)_?(\d*)'), 
                               indexIden=False):
    '''Check if `x` equals `y` (up to indexation).'''
    x, x_i = pattern.search(x).groups()
    y, y_i = pattern.search(y).groups()
    return x == y and (not indexIden or x_i == y_i)


def errorReport(con: str, pres: tuple, depth: int, *, fstream=sys.stdout):
    '''Report an error axiom to `fstream`'''
    print('%sError: %s -> %s' % (depth * ' ' * 4, ', '.join(pres), con))
    if fstream != sys.stdout:
        print('%sError: %s -> %s' % (depth * ' ' * 4, ', '.join(pres), con), file=fstream)


def hasProof(con: list, *pres, fstream=sys.stdout, depth=0, trace=True):
    '''Check if `con` is provable from `pres` by tracing the axiomatic premises.'''
    
    if trace:
        line = '%s<= %s -> %s' % (depth * ' ' * 4, ', '.join(pres), ', '.join(con))
        print(line, file=fstream)
        if fstream != sys.stdout: print(line)

    # multiple conclusions
    if len(con) > 1:
        for c in range(1, len(con)):
            for d in range(len(pres) + 1):
                if (hasProof(con[:c], *pres[:d], fstream=fstream, depth=depth + 1, trace=trace) 
                and hasProof(con[c:], *pres[d:], fstream=fstream, depth=depth + 1, trace=trace)):
                    return True
        else:
            return False
    
    # singe conclusion
    elif len(con) == 1:
        con = con[0]

        # non-atomic conclusion
        if not isatomic(con):
            slash, left, right = bipart(con)
            if slash == '/':
                return hasProof(left, *pres, *right, fstream=fstream, depth=depth + 1, trace=trace)

            elif slash == '\\':
                return hasProof(right, *left, *pres, fstream=fstream, depth=depth + 1, trace=trace)

        # atomic conclusion
        else:
            if len(pres) == 0:
                if trace: errorReport(con, pres, depth, fstream=fstream)
                return False
            else:
                hitNonatomic = False
                for i in range(len(pres)):
                    if not isatomic(pres[i]):
                        hitNonatomic = True
                        slash, left, right = bipart(pres[i])
                        if slash == '/':
                            U = pres[:i]
                            for j in range(i + 1, len(pres) + 1):
                                T, V = pres[i + 1:j], pres[j:]
                                if (hasProof(right, *T, fstream=fstream, depth=depth + 1, trace=trace) 
                                and hasProof([con], *U, *left, *V, fstream=fstream, depth=depth + 1, trace=trace)):
                                    return True
                        elif slash == '\\':
                            V = pres[i + 1:]
                            for j in range(i + 1):
                                U, T = pres[:j], pres[j:i]
                                if (hasProof(left, *T, fstream=fstream, depth=depth + 1, trace=trace) 
                                and hasProof([con], *U, *right, *V, fstream=fstream, depth=depth + 1, trace=trace)):
                                    return True
                else:
                    if len(pres) == 1 and atomicIden(pres[0], con):
                        return True
                    else:
                        if trace and not hitNonatomic: 
                            errorReport(con, pres, depth, fstream=fstream)
                        return False


def selfTest():
    sep = '-' * 10

    print(sep + 'Test 1' + sep)
    con, *pres = ['s'], 's/(np\\s)', '(np\\s)/np', '(s/np)\\s'
    print('%s\n%s\n' % (sep, hasProof(con, *pres)))

    print(sep + 'Test 2' + sep)
    con, *pres = ['s'], 's/(np\\s)', '(np\\s)/np', 's/(np\\s)'
    print('%s\n%s\n' % (sep, hasProof(con, *pres)))


if __name__ == '__main__':
    selfTest()
