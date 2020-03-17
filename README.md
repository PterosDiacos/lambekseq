# LambekSeq

This package is for proving theorems in Categorial grammars (CG) and constructing semantic graphs, i.e., semgraphs on top of that.  

Four CG calculuses are supported here (see below). A "proof" is simply a set of atom links, abstracting away from derivaiton details. Given Atom-Vertex Correspondence, semantic parsing boils down to unifying vertices according to atom links.

## Requirements
Add the path to the package to `PYTHONPATH`.  

Semantic graphs derive from digraph:
- [networkx](https://networkx.github.io/)  

For graph visualization we use
- [Graphviz](https://www.graphviz.org/)
- [python-graphviz](https://github.com/xflr6/graphviz)
- [pydot](https://github.com/xflr6/graphviz)
- [dot2tex](https://dot2tex.readthedocs.io)

## Background

### Categorial grammars:
- Associative Lambek Sequent Calculus Allowing Empty Premises ([Lambek, 1958](https://www.cs.cmu.edu/~fp/courses/15816-f16/misc/Lambek58.pdf))
- Proof Net based on multiplicative fragment of Cyclic Linear Logic ([Pentus, 2010](http://www.aiml.net/volumes/volume8/Pentus.pdf))
- Continuized Combinatory Categorial Grammar ([Barker and Shan, 2014](https://www.oxfordscholarship.com/view/10.1093/acprof:oso/9780199575015.001.0001/acprof-9780199575015))
- Basic Displacement Calculus/Continuized Lambek Calculus ([Morrill et al 2010](https://link.springer.com/article/10.1007/s10849-010-9129-2))

### Semantic graphs:
- Abstract Meaning Representation ([Banarescu et al., 2013](https://www.aclweb.org/anthology/W13-2322/); see also https://github.com/amrisi/amr-guidelines/blob/master/amr.md)
- Hybrid Logic Dependency Semantics ([Baldridge and Kruijff, 2002](https://www.aclweb.org/anthology/P02-1041/); [White, 2006](https://link.springer.com/article/10.1007/s11168-006-9010-2))

