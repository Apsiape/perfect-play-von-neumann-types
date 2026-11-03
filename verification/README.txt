PORTABLE FINITE VERIFICATION

Python 3.10+, standard library only. Keep the four Python modules together.
From any directory:
  python check_type_ladder.py --output-dir NEW_OR_EMPTY_DIRECTORY
The checker refuses a nonempty output directory and writes results exclusively.
run/ contains the current passing results. portability-check.json records
an identical run from relocated sources and a different working directory, plus
the non-overwrite check.

Exact checks cover finite binary trees through depth 7, reader stand-ins through
depth 4, an actual source-lifted graph residual with the scaffold and qutrit
density, fixed-seed group identities, finite shift truncations with their top
boundary defect, and chain scaffold masses through five bridges. Shift entropy
partial sums are checked against the exact geometric-series formula; the
infinite model and limiting entropy are proved in the paper.

The rotation certificate encloses y=1 and y=2, checks the y=3 tail base, and
checks the affine denominator inequality used by the paper's induction. The
induction supplies the all-integer conclusion. The floating sweep is additional
finite evidence. The Boolean checker makes the companion family's finite-host
coordinate unknown for all directional reductions, so the one-bridge separator
carries those exclusions. It also enumerates 7581 monotone Boolean functions.

Finite computations do not prove Higman/HNN embeddings, arbitrary normal-host
extraction, infinite KMS classification or continuous-core classification.
verify_margin_failure.py supplies exact-series helpers and can separately
diagnose the false strict threshold 2.9; it is not the current verification.

SHA256SUMS uses relative bundle paths and LF line endings. Build and visual
evidence refer to the exact main.pdf hash. No local source paths are required.
