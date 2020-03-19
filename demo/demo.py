# %%
from graphviz import Source
from lambekseq.semcomp import SemComp

SemComp.load_lexicon(abbr_path='../abbr.json',
                     vocab_path='../schema.json')

# %%
ex0a = [('a', 'ind'), ('boy', 'n'), 
       ('walked', 'vt'), ('a', 'ind'), ('dog', 'n')]
sc = SemComp(ex0a)
sc.unify()      

# %%
ex0b = [('every', 'qnt'), ('boy', 'n'), 
       ('walked', 'vt'), ('a', 'ind'), ('dog', 'n')]
sc = SemComp(ex0b)
sc.unify()

# %%
ex0c = [('every', 'qnt'), ('boy', 'n'), 
       ('walked', 'vt'), ('a', 'indl'), ('dog', 'n')]
xref0c = [('g4x0', 'g1a0')]
sc = SemComp(ex0c, xref0c)
sc.unify()

# %%
ex1a = [('every', 'qnt'), ('boy', 'n'), 
       ('walked', 'vt'), ('most', 'qnt'), ('dogs', 'n')]
sc = SemComp(ex1a)
sc.unify()

# %%
ex1b = [('every', 'qnt'), ('boy', 'n'), 
       ('walked', 'vt'), ('most', 'qnt'), ('dogs', 'n'),
       ('in', 'pv'), ('every', 'qnt'), ('park', 'n')]
sc = SemComp(ex1b, calc='ccg')
sc.unify()

# %%
ex1c = [('most', 'qnt'), ('voters', 'n'),
        ('from', 'pn'), ('every', 'qnt'), ('state', 'n'),
        ('who', 'rl'), ('voted', 'vi'), ('complained', 'vi')]
sc = SemComp(ex1c)
sc.unify()

# %%
ex2 = [('every', 'qnt'), ('boy', 'n'), 
      ('who', 'rl'), ('walk', 'vt'), ('a', 'ind'), ('dog', 'n'),
      ('fed', 'vt'), ('it', 'pro')]
xref2 = [('g8x0', 'g6a0')]
sc = SemComp(ex2, xref2)
sc.unify()

# %%
ex3 = [('Joe', 'prp'), ('walked', 'vt'), ('and', 'cj'), 
      ('Ben', 'prp'), ('fed', 'vt'), ('his', 'pros'), ('dog', 'n')]
xref3 = [('g6x0', 'g1a0'), ('g6x1', 'g4a0')]
sc = SemComp(ex3, xref3)
sc.unify()

# %%
ex4a = [('Joe', 'prp'), ('ask', 'vco'), ('every', 'qnt'), ('boy', 'n'), 
       ('to', 'nonf'), ('walk', 'vt'), ('a', 'ind'), ('dog', 'n')]
sc = SemComp(ex4a)
sc.unify()

# %%
ex4b = [('Joe', 'prp'), ('ask', 'vco'), ('and', 'cj'), 
        ('Zac', 'prp'), ('want', 'vco'), ('Ben', 'prp'),
       ('to', 'nonf'), ('walk', 'vt'), ('a', 'ind'), ('dog', 'n')]
sc = SemComp(ex4b)
sc.unify()

# %%
ex4c = [('Joe', 'prp'), ('ask', 'vco'), ('Ben', 'prp'), 
        ('and', 'cj'), ('Zac', 'prp'), ('want', 'vco'), ('Dan', 'prp'),
       ('to', 'nonf'), ('walk', 'vt'), ('a', 'ind'), ('dog', 'n')]
sc = SemComp(ex4c)
sc.unify()

# %%
ex5a = [('Joe', 'prp'), ('believe', 'vce'), ('Ben', 'prp'), 
       ('to', 'nonf'), ('walk', 'vt'), ('every', 'qnt'), ('dog', 'n')]
sc = SemComp(ex5a, calc='ccg')
sc.unify()

# %%
ex5b = [('Joe', 'prp'), ('believe', 'vts'), ('Ben', 'prp'), 
       ('walk', 'vt'), ('every', 'qnt'), ('dog', 'n')]
sc = SemComp(ex5b, calc='ccg')
sc.unify()

# %%
ex6 = [('Joe', 'prp'), ('promise', 'vcs'), ('Ben', 'prp'), 
       ('to', 'nonf'), ('walk', 'vt'), ('a', 'ind'), ('dog', 'n')]
sc = SemComp(ex6)
sc.unify()

# %%
ex7 = [('Joe', 'prp'), ('want', 'vtt'),
       ('to', 'nonf'), ('walk', 'vt'), ('a', 'ind'), ('dog', 'n')]
sc = SemComp(ex7)
sc.unify()

# %%
ex8 = [('every', 'qnt'), ('boy', 'n'), ('and', 'cj'),
       ('every', 'qnt'), ('dog', 'n'), ('smile', 'vi')]
sc = SemComp(ex8)
sc.unify()

# %%
ex9 = [('Joe', 'prp'), 
       ('and', 'cj'), ('Ben', 'prp'), 
       ('or', 'dj'), ('Zac', 'prp')]
sc = SemComp(ex9)
sc.unify('np')

# %%
