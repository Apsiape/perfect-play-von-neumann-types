# Perfect play has different arithmetical complexity in semifinite and type III algebras

Seth Douglas and Nidhal Mghirbi. Version 1.0.0, November 2026.

**This is a preprint. It has not been peer reviewed.**

## Abstract

For finite rational nonlocal games, existence of perfect normal play in a type II₁ algebra, a type II∞ algebra, or any semifinite algebra is Σ⁰₂-complete. For each fixed λ∈[0,1], existence in a type IIIλ factor is equivalent to commuting perfection and is Π⁰₁-complete. Existence of commuting perfect play together with absence of every normal semifinite perfect strategy is Π⁰₂-complete. Its hardness holds on a computable family whose every member is commuting perfect and has finite-dimensional quantum value one.

The lower bound combines a critical binary-tree selector, an effective group embedding, and a Boolean compiler on arbitrary faithful normal supports. The selector finds a finite terminal depth even in diffuse semifinite algebras. A finite-corner overlap criterion gives the upper bound. The perfect-play languages for type I and type II₁ are incomparable, and both are proper subsets of the type II∞ language. The type-I complexity used here is established in the companion paper. Two directional differences are D₂(Σ⁰₂)-complete: perfect play in type I but not in type II₁ (I-ONLY), and perfect spatial play attainable only with infinite entropy (INF-ENTROPY-ONLY). For semifinite-but-not-type-I play (II-ONLY) and its finite-entropy variant, completeness remains open; both are Σ⁰₂-hard and Π⁰₂-hard.

## Contents and reproduction

- `paper/main.pdf`: manuscript.
- `paper/`: LaTeX source, bibliography, plain-text abstract, source manifest, source archive and strict build driver. Run `python -B build.py` there with pdflatex and BibTeX installed. Its default creates a new system temporary directory; `--build-dir` selects a new or empty directory. The build uses pdflatex, BibTeX and three further pdflatex passes and rejects warnings, unresolved references and box defects.
- `verification/`: finite checks, recorded outputs and reproduction commands. Start with `verification/README.txt`. Run `python -B check_type_ladder.py --output-dir NEW_OR_EMPTY_DIRECTORY` there.
- `verification/SHA256SUMS`: SHA-256 hashes for every public file except the checksum file itself, with relative paths and LF line endings.
- `paper/source.zip`: relative-path sources, metadata and finite evidence; the compiled PDF and checksum file are external. `paper/source-manifest.json` records the payload paths and hashes. Repackage with `python -B package_sources.py --verification-dir run` from `paper/` after refreshing the build and visual evidence.

Finite computations support the written proofs. They do not establish infinite-dimensional host extraction, group embedding theorems, KMS classification, continuous-core classification or computability conclusions. The cited external sources are identified by DOI in `paper/references.bib` and `verification/provenance-input.json`.

## Citation and rights

See `CITATION.cff` for citation metadata.
Paper and documentation: CC BY 4.0. Scripts: MIT or Apache 2.0, at your option. See `RIGHTS.md`, the license files and `NOTICE`.
