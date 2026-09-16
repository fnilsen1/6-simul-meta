# Session summary

## Current objective

The user restarted the Jupyter notebook from scratch and wants it kept as simple as possible. The current scope is:

1. Generate every unordered six-pin set.
2. Remove sets whose 14×12 move matrix is not full column rank modulo 12.
3. Group the 1,696 survivors directly into equivalence classes by solvability conditions, allowing the eight supplied puzzle orientations.
4. Enumerate all 720 orders of every pin set and sort them within each class by fewest D moves, fewest transitions, then most intuitive moves.
5. Save the best order from each class with its exact eight-orientation scramble coverage percentage.

Do not reintroduce learning orders, coverage flowcharts, or other previous analysis unless the user asks for them again.

## Current files

- `6_simul_pin_sets.ipynb` — simple notebook; 16 cells, 8 code cells.
- `memo_clonk.py` — source of the `pins`, `U`, and `D` definitions.
- `txt/6_simul_pin_sets.txt` — all 3,003 unordered six-pin sets.
- `txt/6_simul_pin_sets_full_rank.txt` — the 1,696 sets that pass the modular-rank test.
- `txt/6_simul_pin_sets_classes.json` — the 54 final classes; each has its count, two conditions, and pin-set list, with no rotation annotations. The conditions correspond to the first listed pin set.
- `txt/6_simul_pin_orders.json` — all 1,221,120 pin orders grouped by class and sorted by fewest D moves, fewest transitions, then most intuitive moves.
- `txt/6_simul_best_pin_orders.json` — the best order from each of the 54 classes, including conditions, D moves, transitions, intuitive moves, and exact scramble percentage.

Older text artifacts from the earlier, more complicated analysis may still exist in `txt/`, but the current notebook does not generate or depend on them.

## Definitions and verified results

Allowed pin names, preserving the source order:

```text
UL UR DR DL U \ L R / D dl dr ur ul
```

`ALL` and `all` are excluded. There are

```text
C(14, 6) = 3003
```

sets.

For a selected six-pin set, its move matrix is formed by concatenating the corresponding six columns from `U` and six columns from `D`. Its shape is 14×12.

Clock arithmetic is modulo 12. A set is accepted exactly when:

```text
rank(A mod 2) = 12
rank(A mod 3) = 12
```

The notebook uses explicit modular Gaussian elimination. It does not use rational or floating-point rank. This leaves exactly 1,696 sets and removes 1,307. The notebook was executed and its assertions passed.

## Condition and rotation grouping

Conditions are computed as the left kernel of each move matrix. Equality is based on the complete equation system modulo 12, rather than on the textual form of two chosen basis equations. The code works modulo 4 and modulo 3, then combines the results with the Chinese remainder theorem. These condition signatures are internal; the notebook outputs only the final rotation-equivalence classes.

For the example `UL UR DR U \\ ur`, the notebook obtains:

- `r - c = 0 (mod 12)`
- `l - u = 0 (mod 12)`

The supplied `z` and `y2` maps are internally consistent: `z^4` and `y2^2` are identity, and `y2 z y2 = z'`. They generate the eight requested orientations and preserve the 1,696-set full-rank pool.

The 1,696 sets form 54 equivalence classes after rotations.

## User preference

Keep explanations and notebook code direct and incremental. The user wants to document the work step by step, adding one stage at a time.
