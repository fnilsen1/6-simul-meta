# Maximum-six-variable inspection flowchart

Estimated coverage across all eight orientations: 44.395850%.

Every four-variable condition has two variables on each side. `A to B` means the clockwise distance from dial A to dial B.

Check the branch equality first. Five of the seven longer conditions become direct distance comparisons and need no separate modulo-12 reduction. Classes 41 and 46 each need one clock sum.

Do not run a separate full flowchart for each angle: record matching dial relationships once, then use `orientation_lookup.json` to match the eight orientations.

```text
START
│
├─ d = c branch
│  ├─ d = r ───────────────────── Class 1
│  ├─ d = u ───────────────────── Class 2
│  ├─ r = u ───────────────────── Class 3
│  ├─ l = u ───────────────────── Class 4
│  ├─ C = D ───────────────────── Class 8
│  ├─ Calculate C to D once
│  │  ├─ U to L = C to D ─────── Class 26
│  │  └─ U to R = C to D ─────── Class 29
│  ├─ UL to U = R + l ────────── Class 41
│  └─ UR to U = L + r ────────── Class 46
│
├─ U = C branch
│  ├─ r = c ───────────────────── Class 10
│  ├─ r = u ───────────────────── Class 11
│  ├─ R to UR = c to l ───────── Class 12
│  ├─ l = u ───────────────────── Class 13
│  ├─ c = l ───────────────────── Class 14
│  ├─ d = r ───────────────────── Class 25
│  └─ d = l ───────────────────── Class 30
│
└─ Adjacent-edge branch
   ├─ L = D
   │  └─ r = u ────────────────── Class 42
   └─ U = L
      ├─ d = r ────────────────── Class 47
      ├─ c to r = l to u ──────── Class 32
      └─ d to r = c to u ──────── Class 33
```

## Learning order and recognition conditions

| Step | Class | Conditions | Marginal | Cumulative |
|---:|---:|---|---:|---:|
| 1 | 4 | d = c; l = u | 5.463700% | 5.463700% |
| 2 | 12 | R to UR = c to l; U = C | 4.760250% | 10.223950% |
| 3 | 41 | UL to U = R + l; d = c | 4.232100% | 14.456050% |
| 4 | 33 | U = L; d to r = c to u | 4.087450% | 18.543500% |
| 5 | 46 | c = d; UR to U = L + r | 3.562150% | 22.105650% |
| 6 | 32 | L = U; c to r = l to u | 3.290100% | 25.395750% |
| 7 | 29 | U to R = C to D; d = c | 2.719750% | 28.115500% |
| 8 | 13 | U = C; l = u | 2.633000% | 30.748500% |
| 9 | 30 | d = l; U = C | 2.165000% | 32.913500% |
| 10 | 26 | U to L = C to D; d = c | 1.857300% | 34.770800% |
| 11 | 25 | U = C; d = r | 1.680050% | 36.450850% |
| 12 | 47 | U = L; d = r | 1.334800% | 37.785650% |
| 13 | 11 | U = C; r = u | 1.329450% | 39.115100% |
| 14 | 3 | d = c; r = u | 1.140300% | 40.255400% |
| 15 | 42 | L = D; r = u | 1.077600% | 41.333000% |
| 16 | 8 | C = D; d = c | 0.795850% | 42.128850% |
| 17 | 1 | d = r; d = c | 0.786800% | 42.915650% |
| 18 | 2 | d = c; d = u | 0.609900% | 43.525550% |
| 19 | 10 | U = C; r = c | 0.439400% | 43.964950% |
| 20 | 14 | c = l; U = C | 0.430900% | 44.395850% |

## Inspection procedure

1. Check the `d = c` and `U = C` edge–center branches. Their rotated forms are the same geometric kind of check, so reuse what you notice across orientations.
2. Test a listed second condition only when its branch equality holds. This avoids doing the four-variable calculations for unrelated states.
3. In the `d = c` branch, reuse `C to D` for both classes 26 and 29.
4. Read the two `to` distances directly from the dials and compare them. Only classes 41 and 46 require a sum (`R + l` or `L + r`), calculated once around the clock face.
5. Separately check the adjacent-edge branch. Classes 42 and 47 need a second equality; classes 32 and 33 compare two distances.
6. Stop at any matching learned case; the branches are not mutually exclusive.
