# %%
from graphviz import Source
from lambekseq.semcomp import SemComp

SemComp.load_lexicon(abbr_path='../abbr.json',
                     vocab_path='../schema.json')

# %%
ex = 'a boy walked a dog'
pos = 'ind n vt ind n'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify()      

# %%
ex = 'every boy walked a dog'
pos = 'qnt n vt ind n'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify()

# %%
ex = 'every boy walked a dog'
pos = 'qnt n vt indl n'
xref = [('g4x0', 'g1a0')]
sc = SemComp(zip(ex.split(), pos.split()), xref)
sc.unify()

# %%
ex = 'every boy walked most dogs'
pos = 'qnt n vt qnt n'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify()

# %%
ex = 'every boy walked most dogs in every park'
pos = 'qnt n vt qnt n pv qnt n'
sc = SemComp(zip(ex.split(), pos.split()), calc='ccg')
sc.unify()

# %%
ex = 'most voters from every state who voted complained'
pos = 'qnt n pn qnt n rl vi vi'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify()

# %%
ex = 'every boy who walked a dog fed it'
pos = 'qnt n rl vt ind n vt pro'
xref = [('g8x0', 'g6a0')]
sc = SemComp(zip(ex.split(), pos.split()), xref)
sc.unify()

# %%
ex = 'Joe walked and Ben fed his dog'
pos = 'prp vt cj prp vt pros n'
xref = [('g6x0', 'g1a0'), ('g6x1', 'g4a0')]
sc = SemComp(zip(ex.split(), pos.split()), xref)
sc.unify()

# %%
ex = 'Joe ask every boy to walk a dog'
pos = 'prp vco qnt n inf vt ind n'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify()

# %%
ex = 'Joe ask and Zac want Ben to walk a dog'
pos = 'prp vco cj prp vco prp inf vt ind n'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify()

# %%
ex = 'Joe ask Ben and Zac want Dan to walk a dog'
pos = 'prp vco prp cj prp vco prp inf vt ind n'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify()

# %%
ex = 'Joe believe Ben to walk every dog'
pos = 'prp vce prp inf vt qnt n'
sc = SemComp(zip(ex.split(), pos.split()), calc='ccg')
sc.unify()

# %%
ex = 'Joe believe Ben walk every dog'
pos = 'prp vts prp vt qnt n'
sc = SemComp(zip(ex.split(), pos.split()), calc='ccg')
sc.unify()

# %%
ex = 'Joe promise Ben to walk a dog'
pos = 'prp vcs prp inf vt ind n'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify()

# %%
ex = 'Joe want to walk a dog'
pos = 'prp vtv inf vt ind n'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify()

# %%
ex = 'every boy and every dog smile'
pos = 'qnt n cj qnt n vi'
sc = SemComp(zip(ex.split(), pos.split()), calc='ccg')
sc.unify()

# %%
ex = 'Joe and Ben or Zac'
pos = 'prp cj prp dj prp'
sc = SemComp(zip(ex.split(), pos.split()))
sc.unify('np')

# %%
