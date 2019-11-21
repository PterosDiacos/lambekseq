import itertools
import math
import collections


def ccgScoping(n):
    '''Return a generator that produces each permutation of n objects generatable from associativity alternatives.
    '''
    def f(T):
        if len(T) == 1:
            yield T
        else:
            for i in range(1, len(T)):
                for l in f(T[:i]):
                    for r in f(T[i:]):
                        yield l + r
                        yield r + l            
    return f(tuple(range(n)))


def compare(n):
    '''Return the difference between all permuations of n objects and their permuations generatable from associativity alternatives.
    '''
    setCCG = set(ccgScoping(n))
    setFac = set(itertools.permutations(range(n)))
    return list(setFac - setCCG)


def catalan_pre(n):
    '''Return the total number of associativity alternatives of n objects.
    '''
    f = math.factorial
    return (2 ** (n-1)) * f(2*n-2)//f(n)//f(n-1)


def stat():
    # do comparison for 2 to 9 objects
    for i in range(2, 10):
        diff = compare(i)
        print(i, math.factorial(i), catalan_pre(i), len(diff), sep='\t')


def ccgRepetitionCount(n):
    L = sorted(list(ccgScoping(n)))
    return collections.Counter(L).most_common()


if __name__ == '__main__':
    for i in range(4, 7):
        D = ccgRepetitionCount(i)
        with open('ccg-%s.txt' % i, 'w') as fout:
            print(*D, sep='\n', file=fout)
