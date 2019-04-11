## Lambek-Sequent-Calculus

The module `lambek2.py` is a simple script for tesiting whether a given category inference pattern is deducible from *Lambek syntactic calculus* (Lambek, 1958). It uses *Lambek sequent calculus* as the decision procedure.

The core function `hasProof` takes two primary arguments:
* `con`: a `list` of conclusions
* `*pres`: one or more premises

Examples of premises and conclusions are currently contained in `lambek2.py` as comments.
