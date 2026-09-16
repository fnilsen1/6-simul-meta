# Four-total-variable inspection flowchart

Estimated coverage across all eight orientations: 31.505900%.

Every learned case is only two equality checks. Do not run a separate full flowchart for each angle: record equal dial groups once, then match those pairs against `orientation_lookup.json`.

```text
START
│
├─ d = c branch
│  ├─ d = r ───────────────────── Class 1
│  ├─ d = u ───────────────────── Class 2
│  ├─ r = u ───────────────────── Class 3
│  ├─ l = u ───────────────────── Class 4
│  └─ C = D ───────────────────── Class 8
│
├─ U = C branch
│  ├─ r = c ───────────────────── Class 10
│  ├─ r = u ───────────────────── Class 11
│  ├─ l = u ───────────────────── Class 13
│  ├─ c = l ───────────────────── Class 14
│  ├─ d = r ───────────────────── Class 25
│  └─ d = l ───────────────────── Class 30
│
└─ Two matching adjacent-edge pairs
   ├─ L = D and r = u ─────────── Class 42
   └─ U = L and d = r ─────────── Class 47
```

## Learning order and canonical conditions

| Step | Class | Conditions | Marginal | Cumulative |
|---:|---:|---|---:|---:|
| 1 | 4 | d - c = 0 (mod 12); l - u = 0 (mod 12) | 5.463700% | 5.463700% |
| 2 | 30 | d - l = 0 (mod 12); U - C = 0 (mod 12) | 4.410650% | 9.874350% |
| 3 | 25 | U - C = 0 (mod 12); d - r = 0 (mod 12) | 3.729300% | 13.603650% |
| 4 | 13 | U - C = 0 (mod 12); l - u = 0 (mod 12) | 3.163400% | 16.767050% |
| 5 | 11 | U - C = 0 (mod 12); r - u = 0 (mod 12) | 2.684500% | 19.451550% |
| 6 | 1 | d - r = 0 (mod 12); d - c = 0 (mod 12) | 2.055400% | 21.506950% |
| 7 | 3 | d - c = 0 (mod 12); r - u = 0 (mod 12) | 2.046400% | 23.553350% |
| 8 | 42 | L - D = 0 (mod 12); r - u = 0 (mod 12) | 1.636600% | 25.189950% |
| 9 | 2 | d - c = 0 (mod 12); d - u = 0 (mod 12) | 1.621150% | 26.811100% |
| 10 | 47 | U - L = 0 (mod 12); d - r = 0 (mod 12) | 1.326500% | 28.137600% |
| 11 | 10 | U - C = 0 (mod 12); r - c = 0 (mod 12) | 1.132100% | 29.269700% |
| 12 | 14 | c - l = 0 (mod 12); U - C = 0 (mod 12) | 1.120750% | 30.390450% |
| 13 | 8 | C - D = 0 (mod 12); d - c = 0 (mod 12) | 1.115450% | 31.505900% |

## Inspection procedure

1. Check the `d = c` and `U = C` edge–center branches. Their rotated forms are the same geometric kind of check, so reuse what you notice across orientations.
2. Test the listed second equality only when its branch equality holds.
3. Separately check the two adjacent-edge-pair patterns for classes 42 and 47.
4. Stop at any matching learned case; the branches are not mutually exclusive.
