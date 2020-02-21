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


def bipart(s: str, 
           leftPr='(', rightPr=')',
           conn={'/', '\\'}):
    '''Break a non-atomic `s` into slashes, the left and right components. 
    The latter two are lists.'''
    s = stripparentheses(s)
    count = 0
    for i in range(len(s)):
        if s[i] == leftPr: count += 1
        elif s[i] == rightPr: count -= 1
        elif count == 0 and s[i] in conn:
            left, right = stripparentheses(s[:i]), stripparentheses(s[i + 1:]) 
            left, right = commaSplit(left), commaSplit(right)
            return s[i], left, right
