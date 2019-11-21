from cmll import ProofNet
from lambek import hasProof
from noprodall import findproof, parseProof


def testLambekSeq(con, pres):
    print('%s\n%s\n' % (
        '-' * 20, hasProof(con, *pres, trace=True)))


def testProofNet(con, pres):
    assert len(con) == 1
    pn = ProofNet.fromLambekSeq(con[0], pres)
    pn.buildProofs()
    pn.printProofLinks()
    print('Total: %d' % pn.proofCount)    


def testNoProdAll(con, pres):
    assert len(con) == 1
    proofs = findproof(con[0], *pres)
    print(*parseProof(proofs), sep='\n')


if __name__ == '__main__':
    #### complex NP island
    # con, *pres = ['n\\n'], '(n\\n)/(s/np)', 'np\\s'
    # con, *pres = ['n\\n'], '(n\\n)/(s/np)', 'np', '(np\\s)/np', 'np/n', 'n', '(n\\n)/(np\\s)', '(np\\s)/np'
    # con, *pres = ['n\\n'], '(n\\n)/(s/np)', 'np', '(np\\s)/np', '(s/(np\\s))/n', 'n', '(n\\n)/(np\\s)', '(np\\s)/np'
    # con, *pres = ['n\\n'], '(n\\n)/(s/np)', '(s/(np\\s))/np'
    # con, *pres = ['n\\n'], '(n\\n)/(s/np)', '(s/(np\\s))/n', 'n', '(n\\n)/(np\\s)', '(np\\s)/np'
    # con, *pres = ['n\\n'], '(n\\n)/(s/np)', '(s/(np\\s))/n', 'n', '(n\\n)/(np\\s)', '(np\\s)/np', '(np\\s)/np', 'np'
    # con, *pres = ['n\\n'], '(n\\n)/(np\\s)', '(s/(np\\s))/n', 'n', '(n\\n)/(np\\s)', '(np\\s)/np', '(np\\s)/np', 'np'
    
    #### PP containing a quantifier followed by a relative clause
    # con, *pres = ['s/((n\\n)\\s)'], '(n\\n)/np', 's/(np\\s)', 'n\\n'
    # con, *pres = ['s/((n\\n)\\s)'], 's/((n\\n)\\s)', 'n\\n'
    # con, *pres = ['(s/n)\\s'], 'n/np', '(s/np)\\s', 'n\\n'
    # con, *pres = ['a/b'], 'a/(np\\s)', '(np\\s)/np', 'np/n', 'n', '(n\\n)/b'
    # con, *pres = ['np'], 'np/n', 'n', '(n\\n)/np', 's/(np\\s)' 
    # con, *pres = ['s/(np\\s)'], '(s/(np\\s))/n', 'n', '(n\\n)/np', 's/(np\\s)'
    # con, *pres = ['s/(n\\s)'], 'n/a', '(s/a)\\s'
    # con, *pres = ['(s/n)\\s'], '(s/n)\\s', 'n\\n'
    # con, *pres = ['s/(n\\s)'], 'n/np', 's/(np\\s)'
    # con, *pres = ['s/(n\\s)'], 'n/np', 's/(np\\s)', 'n\\n'
    # con, *pres = ['s/(n\\s)'], 's/(n\\s)', 'n\\n'           
 
    #### "student from every department who failed"
    # con, *pres = ['(s/n)\\s'], 'n/np', '(s/np)\\s'
    # con, *pres = ['(s/(np,n\\n))\\s'], '(s/np)\\s', 'n\\n'
    # con, *pres = ['(s/n)\\s'], 'n/np', '(s/(np,n\\n))\\s'
    # con, *pres = ['(s/n)\\s'], 'n/np', 's/(np\\s)', 'n\\n'
    # con, *pres = ['s/((x,n\\n)\\s)'], 's/(x\\s)', 'n\\n'
    # con, *pres = ['(s/np)\\s'], 's/(np\\s)', '((np\\s)\\(np\\s))/np', 's/(np\\s)'
   
    # con, *pres = ['np\\q'], '(np\\s)/np', '(q/np)\\s', '((np\\s)\\(np\\s))/np', 's/(np\\s)'
    # con, *pres = ['np\\s'], '(wnp\\ws)/np', 's/(np\\s)', '((wnp\\ws)\\(np\\x))/y', '(x/y)\\s'    
    # con, *pres = ['dnp\\q'], '(wnp\\ws)/np', '(s/np)\\s', '((wnp\\ws)\\(dnp\\x))/y', '(x/y)\\q'

    #### "believe every boy walked a dog"
    # con, *pres = ['a/((np,np\\b)\\s)'], 'a/(np\\s)', 'np\\b'
    # con, *pres = ['(a/(np,np\\b))\\s'], '(a/np)\\s', 'np\\b'
    # con, *pres = ['(s/(np,np\\s))\\s'], '(s/np)\\s', 'np\\s'
    # con, *pres = ['np\\s'], 'np\\(a/b)', '(a/(np,np\\b))\\s'
    # con, *pres = ['np\\s'], 'np\\(a/b)', 'a/(np\\s)', 'np\\b'
    # con, *pres = ['np\\s'], 'np\\(a/b)', '(a/np)\\s', 'np\\b'
    # con, *pres = ['np\\s'], '(np\\s)/np', 's'

    #### "ben believes every boy to walk a dog"
    # con, *pres = ['(s/np)\\(s/np)'], '(s/(np\\s))/np'
    # con, *pres = ['np\\((s/(np\\s))/np)'], '((np\\s)/(np\\s))/np'
    
    #### crossing
    # con, *pres = ['np_0\\(np_1\\(np_2\\s_3))'], '(np_4\\(np_5\\s_6))/(np_7\\s_8)', 'np_9\\(np_10\\s_11)'
    # con, *pres = ['s_0'], 'np_1', 'np_2', 'np_3', 's_4\\(np_5\\s_6)', 'np_7\\(np_8\\s_9)'
    # con, *pres = ['np_0\\(np_1\\(np_2\\(np_3\\s_4)))'], '(np_5\\(np_6\\s_7))/(np_8\\s_9)', 'np_10\\(np_11\\(np_12\\s_13))'
    
    #### dev
    # con, *pres = ['s_0'], 's_1/(np_2\\s_3)', '(np_4\\s_5)/np_6', 's_7/(np_8\\s_9)'
    con, *pres = ['s_0'], 's_1/(np_2\\s_3)', '(np_4\\s_5)/np_6', '(s_7/np_8)\\s_9'
    # con, *pres = ['np_0\\s_1'], '(np_2\\s_3)/np_4', 's_5/(np_6\\s_7)'
    # con, *pres = ['np_0\\s_1'], '(np_2\\s_3)/np_4', '(s_5/np_6)\\s_7'
    # con, *pres = ['(s_0/np_1)\\s_2'], 's_3/(np_4\\s_5)'
    # con, *pres = ['s_0/(np_1\\s_2)'], 'np_3' 

    # testProofNet(con, pres)
    # testLambekSeq(con, pres)

    testNoProdAll(con, pres)