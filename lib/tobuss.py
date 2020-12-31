'''Utilities for translating lambek calculus proof tree
into Bussproofs Latex code (https://ctan.org/pkg/bussproofs).

Use `toBuss` function:
    - `con`:     conclusion
    - `pres`:    a list of premises
    - `tree`:    accessible at `LambekProof/DisplaceProof` instances.
'''

import re


ESCAPE_MAP = {'\\': '\\textbackslash ',
              '^': '\\text{$\\uparrow$}',
              '!': '\\text{$\\downarrow$}',
              '$': '_{\\$}',
              '&': '_{\\&}'}


def trans_term(s,
    inMath=False,
    font='it',
    pat0=re.compile(r'(?<=\A)-(?=\Z)'),
    pat1=re.compile('|'.join(re.escape(c) for c in ESCAPE_MAP)),
    pat2=re.compile(r'(\w+)_(\d+)')):

    s = pat0.sub('[]', s)
    s = pat1.sub(lambda m: ESCAPE_MAP[m.group(0)], s)
    s = pat2.sub(lambda m: '{\\%s' % font + '%s}_{%s}' % m.groups(), s)
    if not inMath: s = '$%s$' % s
    return s


def trans_law(con, pres):
    trans_pres = map(trans_term, pres)
    trans_con = trans_term(con) 
    return '%s $\\to$ %s' % (
        '\\enskip{}'.join(trans_pres), trans_con)


def axiom_line(con, pres, indent=''):
    return '%s\\AXC{%s}\n' %  (
        indent, trans_law(con, pres))


def unary_infer(above, con, pres, indent=''):
    return '%s%s\\UIC{%s}\n' % (
        above, indent, trans_law(con, pres))


def binary_infer(above1, above2, con, pres, indent=''):
    return '%s%s%s\\BIC{%s}\n' % (
        above1, above2, indent, trans_law(con, pres))


def toBuss(con, pres, tree, proofs, 
           indent='', space=' ' * 4):
    res = ''
    key = con, *pres
    for links in proofs:
        if not indent:
            s = sorted('(%s, %s)' % (i, j) for (i, j) in links)
            res += ', '.join(s) + '\n' + '-' * 10 + '\n'
            res += '\\begin{prooftree}\n\\EnableBpAbbreviations\n'

        if (key, links) in tree:
            if len(tree[key, links]) == 2:
                sub1, sub2 = tree[key, links]
                res += binary_infer(
                    toBuss(sub1[0][0], sub1[0][1:], 
                        tree, [sub1[1]], indent + space),
                    toBuss(sub2[0][0], sub2[0][1:], 
                        tree, [sub2[1]], indent + space),
                    con, pres, indent)
            elif len(tree[key, links]) == 1:
                sub, = tree[key, links]
                res += unary_infer(
                    toBuss(sub[0][0], sub[0][1:], 
                        tree, [sub[1]], indent + space),
                    con, pres, indent)
        else:
            res += axiom_line(con, pres, indent)

        if not indent:
            res += '\\end{prooftree}\n\n\n'

    return res
