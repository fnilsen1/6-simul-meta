# Maximum-eight-term inspection flowchart

Estimated coverage across all eight orientations: 49.235000%.

A coefficient such as `2c` counts as one term. Every four-term equation has two variables on each side. `A to B` means the clockwise distance from dial A to dial B.

Check the simple equality gate before its longer conditions. Classes 22, 24, and 28 reuse both `d = c` and `U to UL`. Class 31 is two direct distance comparisons.

Do not run a separate full flowchart for each angle: record matching dial relationships once, then use `orientation_lookup.json` to match the eight orientations.

```text
START
│
├─ d = c branch
│  ├─ d = r ───────────────────────── Class 1
│  ├─ d = u ───────────────────────── Class 2
│  ├─ r = u ───────────────────────── Class 3
│  ├─ l = u ───────────────────────── Class 4
│  ├─ C = D ───────────────────────── Class 8
│  ├─ Calculate C to D once
│  │  ├─ U to L = C to D ─────────── Class 26
│  │  └─ U to R = C to D ─────────── Class 29
│  ├─ UL to U = R + l ────────────── Class 41
│  ├─ UR to U = L + r ────────────── Class 46
│  └─ Calculate U to UL once
│     ├─ U to UL = (UR + 2c) to u ─── Class 22
│     ├─ U to UL = (UR + r + c) to u ─ Class 24
│     └─ U to UL = (UR + d + l) to u ─ Class 28
│
├─ U = C branch
│  ├─ r = c ───────────────────────── Class 10
│  ├─ r = u ───────────────────────── Class 11
│  ├─ R to UR = c to l ───────────── Class 12
│  ├─ l = u ───────────────────────── Class 13
│  ├─ c = l ───────────────────────── Class 14
│  ├─ d = r ───────────────────────── Class 25
│  └─ d = l ───────────────────────── Class 30
│
├─ Adjacent-edge branch
│  ├─ L = D
│  │  └─ r = u ────────────────────── Class 42
│  └─ U = L
│     ├─ d = r ────────────────────── Class 47
│     ├─ c to r = l to u ──────────── Class 32
│     └─ d to r = c to u ──────────── Class 33
│
└─ Two-distance branch
   └─ C to U = D to R
      └─ d to c = l to u ──────────── Class 31
```

## Learning order and recognition conditions

| Step | Class | Conditions | Marginal | Cumulative |
|---:|---:|---|---:|---:|
| 1 | 4 | d = c; l = u | 5.463700% | 5.463700% |
| 2 | 28 | d = c; U to UL = (UR + d + l) to u | 4.765900% | 10.229600% |
| 3 | 22 | c = d; U to UL = (UR + 2c) to u | 4.272800% | 14.502400% |
| 4 | 32 | L = U; c to r = l to u | 4.091800% | 18.594200% |
| 5 | 24 | c = d; U to UL = (UR + r + c) to u | 3.655250% | 22.249450% |
| 6 | 33 | U = L; d to r = c to u | 3.303900% | 25.553350% |
| 7 | 12 | R to UR = c to l; U = C | 3.046700% | 28.600050% |
| 8 | 41 | UL to U = R + l; d = c | 2.773650% | 31.373700% |
| 9 | 46 | c = d; UR to U = L + r | 2.400200% | 33.773900% |
| 10 | 30 | d = l; U = C | 1.941100% | 35.715000% |
| 11 | 29 | U to R = C to D; d = c | 1.829500% | 37.544500% |
| 12 | 13 | U = C; l = u | 1.642300% | 39.186800% |
| 13 | 31 | C to U = D to R; d to c = l to u | 1.509250% | 40.696050% |
| 14 | 47 | U = L; d = r | 1.391900% | 42.087950% |
| 15 | 26 | U to L = C to D; d = c | 1.309800% | 43.397750% |
| 16 | 25 | U = C; d = r | 1.139850% | 44.537600% |
| 17 | 42 | L = D; r = u | 1.067150% | 45.604750% |
| 18 | 11 | U = C; r = u | 0.977550% | 46.582300% |
| 19 | 3 | d = c; r = u | 0.846450% | 47.428750% |
| 20 | 1 | d = r; d = c | 0.543850% | 47.972600% |
| 21 | 8 | C = D; d = c | 0.428900% | 48.401500% |
| 22 | 2 | d = c; d = u | 0.328350% | 48.729850% |
| 23 | 10 | U = C; r = c | 0.255300% | 48.985150% |
| 24 | 14 | c = l; U = C | 0.249850% | 49.235000% |

## Inspection procedure

1. Check the `d = c` and `U = C` edge–center branches and reuse matching relationships across orientations.
2. Within `d = c`, check the direct equalities first, then reuse `C to D` for classes 26 and 29.
3. Reuse `U to UL` for classes 22, 24, and 28. Only the parenthesized starting position changes.
4. Check the adjacent-edge branch, then the two distances for class 31.
5. The branches are not mutually exclusive; stop at any matching learned case.
