import sys


def stripparentheses(s: str, leftPr='(', rightPr=')'):
    '''Remove redundant parentheses in `s`.'''
    s = s.strip()
    count = 0
    if s.startswith(leftPr):
        for i in range(len(s)):
            if s[i] == leftPr:
                count += 1
            elif s[i] == rightPr:
                count -= 1
                if count == 0 and i < len(s) -1: return s
        else:
            return stripparentheses(s[1:-1], leftPr)
    else:
        return s


def isatomic(s: str):
    '''Check if `s` is atomic.'''
    return not ('/' in s or '\\' in s)


def commaSplit(s: str):
    '''Split `s` at its top-level commas.'''
    count = 0
    for i in range(len(s)):
        if s[i] == '(':
            count += 1
        elif s[i] == ')':
            count -= 1
        elif s[i] == ',':
            if count == 0: return [s[:i]] + commaSplit(s[i + 1:])
    else:
        return [s]


def bipart(s: str):
    '''Break a non-atomic `s` into slashes, the left, and right components.'''
    s = stripparentheses(s)
    count = 0
    for i in range(len(s)):
        if s[i] == '(':
            count += 1
        elif s[i] == ')':
            count -= 1
        elif count == 0 and s[i] in ['/', '\\']:
            left, right = stripparentheses(s[:i]), stripparentheses(s[i + 1:]) 
            left, right = commaSplit(left), commaSplit(right)
            return s[i], left, right


def errorReport(con: str, pres: tuple, *, fstream=sys.stdout):
    '''Report an error axiom to `fstream`'''
    print('Failed attempt: %s -> %s' % (', '.join(pres), con))
    if fstream != sys.stdout:
        print('Failed attempt: %s -> %s' % (', '.join(pres), con), file=fstream)


def hasProof(con: list, *pres, fstream=sys.stdout, depth=0, trace=True):
    '''Check if `con` is provable from `pres` by tracing the axiomatic premises.'''
    
    if trace:
        print('%s <= %s -> %s' % (depth * ' ' * 4, ', '.join(pres), ', '.join(con)), file=fstream)
        if fstream != sys.stdout:
            print('%s <= %s -> %s' % (depth * ' ' * 4, ', '.join(pres), ', '.join(con)))

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
                errorReport(con, pres, fstream=fstream)
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
                    if len(pres) == 1 and (pres[0] == con or {pres[0], con} == {'s', 'np'}):
                        return True
                    else:
                        if not hitNonatomic: errorReport(con, pres, fstream=fstream)
                        return False


if __name__ == '__main__':
    #### Complex NP island
    # con, *pres = ['n\\n'], '(n\\n)/(s/np)', '(s/(np\\s))/np'
    # con, *pres = ['n\\n'], '(n\\n)/(s/np)', '(s/(np\\s))/n', 'n', '(n\\n)/(np\\s)', '(np\\s)/np'
    # con, *pres = ['n\\n'], '(n\\n)/(s/np)', '(s/(np\\s))/n', 'n', '(n\\n)/(np\\s)', '(np\\s)/np', '(np\\s)/np', 'np'
    # con, *pres = ['n\\n'], '(n\\n)/(np\\s)', '(s/(np\\s))/n', 'n', '(n\\n)/(np\\s)', '(np\\s)/np', '(np\\s)/np', 'np'
    
    #### PP containing a quantifier followed by a relative clause
    # con, *pres = ['s/((n\\n)\\s)'], '(n\\n)/np', 's/(np\\s)', 'n\\n'
    # con, *pres = ['s/((n\\n)\\s)'], 's/((n\\n)\\s)', 'n\\n'
    
    #### Quantifier
    # con, *pres = ['a/b'], 'a/(np\\s)', '(np\\s)/np', 'np/n', 'n', '(n\\n)/b'
    # con, *pres = ['np'], 'np/n', 'n', '(n\\n)/np', 's/(np\\s)' 
    # con, *pres = ['s/(np\\s)'], '(s/(np\\s))/n', 'n', '(n\\n)/np', 's/(np\\s)'
    # con, *pres = ['(s/n)\\s'], 'n/np', '(s/np)\\s'
    # con, *pres = ['(s/n)\\s'], 'n/np', '(s/np)\\s', 'n\\n'
    # con, *pres = ['(s/n)\\s'], '(s/n)\\s', 'n\\n'
    # con, *pres = ['s/(n\\s)'], 'n/np', 's/(np\\s)'
    # con, *pres = ['s/(n\\s)'], 'n/np', 's/(np\\s)', 'n\\n'
    # con, *pres = ['s/(n\\s)'], 's/(n\\s)', 'n\\n'           
 
    #### "student from every department who failed"
    # con, *pres = ['(s/(np,n\\n))\\s'], '(s/np)\\s', 'n\\n'
    # con, *pres = ['(s/n)\\s'], 'n/np', '(s/(np,n\\n))\\s'
    # con, *pres = ['(s/np)\\s'], 's/(np\\s)', '((np\\s)\\(np\\s))/np', 's/(np\\s)'
   
    con, *pres = ['np\\q'], '(np\\s)/np', '(q/np)\\s', '((np\\s)\\(np\\s))/np', 's/(np\\s)'
    # con, *pres = ['np\\s'], '(wnp\\ws)/np', 's/(np\\s)', '((wnp\\ws)\\(np\\x))/y', '(x/y)\\s'    
    
    # con, *pres = ['dnp\\q'], '(wnp\\ws)/np', '(s/np)\\s', '((wnp\\ws)\\(dnp\\x))/y', '(x/y)\\q'

    print('%s\n%s' % ('-' * 50, hasProof(con, *pres, trace=True, fstream=open('log.log', 'w'))))
