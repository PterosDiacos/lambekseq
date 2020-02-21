'''Lambek sequent calculus with products in conclusion.
This script finds one proof with all inferential steps.
'''
import sys
from parentheses import bipart, isatomic, atomicIden


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
                    if len(pres) == 1 and isatomic(pres[0]) and atomicIden(pres[0], con):
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
