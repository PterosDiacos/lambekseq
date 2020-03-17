# Lambekseq

This package is for proving theorems in Categorial grammars (CG) and constructing semantic graphs, i.e., semgraphs on top of that.  

Three CG calculuses are supported here (see below). A "proof" is simply a set of atom links, abstracting away from derivaiton details.

## Requirements
Add the path to the package to `PYTHONPATH`. None of the below packages is needed to use the theorem proving facility.

Semantic graphs derive from digraph:
- [networkx](https://networkx.github.io/)  

For graph visualization we use
- [pydot](https://github.com/xflr6/graphviz) (required by `networkx`)
- [Graphviz](https://www.graphviz.org/)
- [python-graphviz](https://github.com/xflr6/graphviz)
- [dot2tex](https://dot2tex.readthedocs.io)

## Background

### Categorial grammars:
- Associative Lambek Calculus Allowing Empty Premises ([Lambek 1958](https://www.cs.cmu.edu/~fp/courses/15816-f16/misc/Lambek58.pdf))
- Proof Net for Lambek Calculus based on Cyclic Multiplicative Linear Logic ([Pentus 2010](http://www.aiml.net/volumes/volume8/Pentus.pdf))
- Continuized Combinatory Categorial Grammar ([Barker and Shan 2014](https://www.oxfordscholarship.com/view/10.1093/acprof:oso/9780199575015.001.0001/acprof-9780199575015))
- Basic Displacement Calculus/Continuized Lambek Calculus ([Morrill et al 2010](https://link.springer.com/article/10.1007/s10849-010-9129-2))

### Semantic graphs:
- Abstract Meaning Representation ([Banarescu et al 2013](https://www.aclweb.org/anthology/W13-2322/);  
see also https://github.com/amrisi/amr-guidelines/blob/master/amr.md)
- Hybrid Logic Dependency Semantics ([Baldridge and Kruijff 2002](https://www.aclweb.org/anthology/P02-1041/); [White 2006](https://link.springer.com/article/10.1007/s11168-006-9010-2))


## Theorem Proving
To prove a theorem, use `atomlink` module. For example, using Lambek Calculus to prove `s np\s -> s`.
```
>>> import lambekseq.atomlink as al

>>> con, *pres = 's', 'np', 'np\\s'
>>> con, pres, parser, _ = al.searchLinks(al.LambekProof, con, pres)
>>> al.printLinks(con, pres, parser)
```
This outputs
```
s_0 <= np_1 np_2\s_3

(np_1, np_2), (s_0, s_3)

Total: 1
```

You can run `atomlink` in command line. The following finds proofs for the **first** themorem in `input.json`, using abbreviation definitions in `abbr.json` and Basic Displacement Calculus.

```
$ python atomlink.py -j input.json -a abbr.json -c dsp
```

Run `python atomlink.py --help` for details.

## Semantic Parsing
