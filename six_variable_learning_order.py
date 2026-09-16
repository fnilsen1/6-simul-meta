LEARNING_ORDER_CONFIG = globals().get("_learning_order_config", {})
MAX_CONDITION_TERMS = LEARNING_ORDER_CONFIG.get("max_condition_terms", 6)
COUNT_COEFFICIENT_REPETITIONS = LEARNING_ORDER_CONFIG.get(
    "count_coefficient_repetitions", True
)
EXPECTED_CLASS_COUNT = LEARNING_ORDER_CONFIG.get("expected_class_count", 20)
FOLDER_NAME = LEARNING_ORDER_CONFIG.get(
    "folder_name", "6_total_variables_learning_order"
)
FLOWCHART_NAME = LEARNING_ORDER_CONFIG.get(
    "flowchart_name", "Maximum-six-variable"
)

LEARNING_ORDER_DIR = OUTPUT_DIR / FOLDER_NAME
LEARNING_ORDER_DIR.mkdir(exist_ok=True)


def condition_variable_count(row):
    """Count terms using the rule selected for this learning-order folder."""
    if not COUNT_COEFFICIENT_REPETITIONS:
        return int(np.count_nonzero(np.asarray(row) % 12))
    signed = ((np.asarray(row, dtype=int) + 6) % 12) - 6
    return int(np.abs(signed).sum())


def recognition_condition(row):
    """Format a condition as equal dial values or two-variable sides."""
    positive = []
    negative = []
    for coefficient, name in zip(row, state_names):
        coefficient = ((int(coefficient) + 6) % 12) - 6
        if coefficient > 0:
            positive.extend([name] * coefficient)
        elif coefficient < 0:
            negative.extend([name] * -coefficient)

    if len(positive) == len(negative) == 1:
        return f"{positive[0]} = {negative[0]}", 0

    # p1 + p2 = n1 + n2 becomes n1-to-p1 = p2-to-n2.
    # Both sides are read directly as clockwise distances on the clock.
    if len(positive) == len(negative) == 2:
        return (
            f"{negative[0]} to {positive[0]} = "
            f"{positive[1]} to {negative[1]}",
            0,
        )

    # A one-versus-three split cannot become two distances without adding a
    # new variable. Keep exactly two variables on each side and use one sum.
    if len(positive) == 1 and len(negative) == 3:
        return (
            f"{negative[0]} to {positive[0]} = "
            f"{negative[1]} + {negative[2]}",
            1,
        )
    if len(positive) == 3 and len(negative) == 1:
        return (
            f"{positive[0]} + {positive[1]} = "
            f"{positive[2]} to {negative[0]}",
            1,
        )

    left = " + ".join(positive) if positive else "0"
    right = " + ".join(negative) if negative else "0"
    return f"{left} = {right}", 1


saved_best_cases = json.loads(
    (OUTPUT_DIR / "6_simul_best_pin_orders.json").read_text(encoding="utf-8")
)["classes"]
best_case_by_number = {case["class"]: case for case in saved_best_cases}

six_variable_cases = []
for class_data in classes:
    best_case = best_case_by_number[class_data["class"]]
    best_pin_set = tuple(sorted(best_case["best_pin_order"], key=pin_order.get))
    displayed_basis = condition_bases[best_pin_set]
    first_count, second_count = [
        condition_variable_count(row) for row in displayed_basis
    ]
    if first_count + second_count <= MAX_CONDITION_TERMS:
        formatted_conditions = [
            recognition_condition(row) for row in displayed_basis
        ]
        recognition_conditions = [condition for condition, _ in formatted_conditions]
        # This pairing lets classes 26 and 29 reuse the same C-to-D distance.
        if class_data["class"] == 29:
            recognition_conditions[0] = "U to R = C to D"
        if class_data["class"] == 22:
            recognition_conditions[1] = "U to UL = (UR + 2c) to u"
        if class_data["class"] == 24:
            recognition_conditions[1] = "U to UL = (UR + r + c) to u"
        if class_data["class"] == 28:
            recognition_conditions[1] = "U to UL = (UR + d + l) to u"
        six_variable_cases.append({
            "class": class_data["class"],
            "best_pin_order": best_case["best_pin_order"],
            "conditions": recognition_conditions,
            "condition_variable_counts": [first_count, second_count],
            "total_condition_variables": first_count + second_count,
            "clock_sum_calculations": sum(count for _, count in formatted_conditions),
            "d_moves": best_case["d_moves"],
            "transitions": best_case["transitions"],
            "intuitive_moves": best_case["intuitive_moves"],
            "standalone_percentage": best_case["scrambles_solved_percentage"],
            "representative": tuple(class_data["pin_sets"][0]),
        })

assert len(six_variable_cases) == EXPECTED_CLASS_COUNT

# Build each class's union over all eight orientations.
system_by_signature = {}
case_signatures = []
for case in six_variable_cases:
    signatures = []
    for _, rotated in oriented_pin_sets(case["representative"]):
        signature = condition_signatures[rotated]
        system_by_signature.setdefault(signature, condition_bases[rotated])
        if signature not in signatures:
            signatures.append(signature)
    case_signatures.append(signatures)

system_signatures = list(system_by_signature)
system_index = {signature: index for index, signature in enumerate(system_signatures)}
condition_rows = np.stack([
    system_by_signature[signature] for signature in system_signatures
]).reshape(-1, 14).astype(np.int16)
case_system_indices = [
    np.asarray([system_index[signature] for signature in signatures])
    for signatures in case_signatures
]

# A shared sample makes every marginal-coverage comparison consistent.
sample_count = 2_000_000
batch_size = 5_000
rng = np.random.default_rng(20260912)
solved_by_case = np.empty((len(six_variable_cases), sample_count), dtype=bool)

for start in range(0, sample_count, batch_size):
    stop = min(start + batch_size, sample_count)
    states = rng.integers(0, 12, size=(stop - start, 14), dtype=np.int16)
    values = (condition_rows @ states.T) % 12
    solved_by_system = np.all(
        values.reshape(len(system_signatures), 2, stop - start) == 0,
        axis=1,
    )
    for case_index, indices in enumerate(case_system_indices):
        solved_by_case[case_index, start:stop] = np.any(
            solved_by_system[indices], axis=0
        )

# Greedily maximize new coverage. Move ergonomics break exact ties.
covered = np.zeros(sample_count, dtype=bool)
remaining = set(range(len(six_variable_cases)))
learning_order = []
while remaining:
    choice = max(
        remaining,
        key=lambda index: (
            np.count_nonzero(solved_by_case[index] & ~covered),
            -six_variable_cases[index]["d_moves"],
            -six_variable_cases[index]["transitions"],
            six_variable_cases[index]["intuitive_moves"],
            -six_variable_cases[index]["class"],
        ),
    )
    new_states = solved_by_case[choice] & ~covered
    covered |= solved_by_case[choice]
    remaining.remove(choice)

    case = dict(six_variable_cases[choice])
    case.pop("representative")
    case["step"] = len(learning_order) + 1
    case["marginal_percentage"] = round(
        100 * np.count_nonzero(new_states) / sample_count, 6
    )
    case["cumulative_percentage"] = round(
        100 * np.count_nonzero(covered) / sample_count, 6
    )
    learning_order.append(case)

learning_result = {
    "description": f"Greedy marginal-coverage order for classes with at most {MAX_CONDITION_TERMS} total condition terms",
    "all_eight_orientations": True,
    "coverage_method": "2,000,000 uniformly sampled states; overlaps counted once",
    "condition_complexity_definition": (
        "sum of variable occurrences across both equations; repeated variables "
        "and coefficient magnitudes are counted repeatedly"
        if COUNT_COEFFICIENT_REPETITIONS else
        "sum of nonzero terms across both equations; a coefficient such as 2c counts as one term"
    ),
    "condition_display": "four-variable conditions have two variables on each side; 'A to B' means the clockwise distance from dial A to dial B",
    "class_count": len(learning_order),
    "coverage_percentage": learning_order[-1]["cumulative_percentage"],
    "classes": learning_order,
}
(LEARNING_ORDER_DIR / "learning_order.json").write_text(
    json.dumps(learning_result, indent=2) + "\n",
    encoding="utf-8",
)

# Store every rotated form, so inspection does not require rerunning a
# canonical flowchart from scratch after physically rotating the clock.
orientation_lookup = []
for learned_case in learning_order:
    entries = []
    for orientation_name, moves in orientations:
        rotated_order = list(learned_case["best_pin_order"])
        for move in moves:
            rotated_order = [move[name] for name in rotated_order]
        entries.append({
            "orientation": orientation_name,
            "pin_order": rotated_order,
        })
    orientation_lookup.append({
        "step": learned_case["step"],
        "class": learned_case["class"],
        "conditions": learned_case["conditions"],
        "best_pin_order": learned_case["best_pin_order"],
        "orientations": entries,
    })

(LEARNING_ORDER_DIR / "orientation_lookup.json").write_text(
    json.dumps({"classes": orientation_lookup}, indent=2) + "\n",
    encoding="utf-8",
)

if MAX_CONDITION_TERMS == 8:
    flowchart_lines = [
        f"# {FLOWCHART_NAME} inspection flowchart",
        "",
        f"Estimated coverage across all eight orientations: {learning_result['coverage_percentage']:.6f}%.",
        "",
        "A coefficient such as `2c` counts as one term. Every four-term equation has two variables on each side. `A to B` means the clockwise distance from dial A to dial B.",
        "",
        "Check the simple equality gate before its longer conditions. Classes 22, 24, and 28 reuse both `d = c` and `U to UL`. Class 31 is two direct distance comparisons.",
        "",
        "Do not run a separate full flowchart for each angle: record matching dial relationships once, then use `orientation_lookup.json` to match the eight orientations.",
        "",
        "```text",
        "START",
        "│",
        "├─ d = c branch",
        "│  ├─ d = r ───────────────────────── Class 1",
        "│  ├─ d = u ───────────────────────── Class 2",
        "│  ├─ r = u ───────────────────────── Class 3",
        "│  ├─ l = u ───────────────────────── Class 4",
        "│  ├─ C = D ───────────────────────── Class 8",
        "│  ├─ Calculate C to D once",
        "│  │  ├─ U to L = C to D ─────────── Class 26",
        "│  │  └─ U to R = C to D ─────────── Class 29",
        "│  ├─ UL to U = R + l ────────────── Class 41",
        "│  ├─ UR to U = L + r ────────────── Class 46",
        "│  └─ Calculate U to UL once",
        "│     ├─ U to UL = (UR + 2c) to u ─── Class 22",
        "│     ├─ U to UL = (UR + r + c) to u ─ Class 24",
        "│     └─ U to UL = (UR + d + l) to u ─ Class 28",
        "│",
        "├─ U = C branch",
        "│  ├─ r = c ───────────────────────── Class 10",
        "│  ├─ r = u ───────────────────────── Class 11",
        "│  ├─ R to UR = c to l ───────────── Class 12",
        "│  ├─ l = u ───────────────────────── Class 13",
        "│  ├─ c = l ───────────────────────── Class 14",
        "│  ├─ d = r ───────────────────────── Class 25",
        "│  └─ d = l ───────────────────────── Class 30",
        "│",
        "├─ Adjacent-edge branch",
        "│  ├─ L = D",
        "│  │  └─ r = u ────────────────────── Class 42",
        "│  └─ U = L",
        "│     ├─ d = r ────────────────────── Class 47",
        "│     ├─ c to r = l to u ──────────── Class 32",
        "│     └─ d to r = c to u ──────────── Class 33",
        "│",
        "└─ Two-distance branch",
        "   └─ C to U = D to R",
        "      └─ d to c = l to u ──────────── Class 31",
        "```",
        "",
        "## Learning order and recognition conditions",
        "",
        "| Step | Class | Conditions | Marginal | Cumulative |",
        "|---:|---:|---|---:|---:|",
    ]
else:
    flowchart_lines = [
    f"# {FLOWCHART_NAME} inspection flowchart",
    "",
    f"Estimated coverage across all eight orientations: {learning_result['coverage_percentage']:.6f}%.",
    "",
    "Every four-variable condition has two variables on each side. `A to B` means the clockwise distance from dial A to dial B.",
    "",
    "Check the branch equality first. Five of the seven longer conditions become direct distance comparisons and need no separate modulo-12 reduction. Classes 41 and 46 each need one clock sum.",
    "",
    "Do not run a separate full flowchart for each angle: record matching dial relationships once, then use `orientation_lookup.json` to match the eight orientations.",
    "",
    "```text",
    "START",
    "│",
    "├─ d = c branch",
    "│  ├─ d = r ───────────────────── Class 1",
    "│  ├─ d = u ───────────────────── Class 2",
    "│  ├─ r = u ───────────────────── Class 3",
    "│  ├─ l = u ───────────────────── Class 4",
    "│  ├─ C = D ───────────────────── Class 8",
    "│  ├─ Calculate C to D once",
    "│  │  ├─ U to L = C to D ─────── Class 26",
    "│  │  └─ U to R = C to D ─────── Class 29",
    "│  ├─ UL to U = R + l ────────── Class 41",
    "│  └─ UR to U = L + r ────────── Class 46",
    "│",
    "├─ U = C branch",
    "│  ├─ r = c ───────────────────── Class 10",
    "│  ├─ r = u ───────────────────── Class 11",
    "│  ├─ R to UR = c to l ───────── Class 12",
    "│  ├─ l = u ───────────────────── Class 13",
    "│  ├─ c = l ───────────────────── Class 14",
    "│  ├─ d = r ───────────────────── Class 25",
    "│  └─ d = l ───────────────────── Class 30",
    "│",
    "└─ Adjacent-edge branch",
    "   ├─ L = D",
    "   │  └─ r = u ────────────────── Class 42",
    "   └─ U = L",
    "      ├─ d = r ────────────────── Class 47",
    "      ├─ c to r = l to u ──────── Class 32",
    "      └─ d to r = c to u ──────── Class 33",
    "```",
    "",
    "## Learning order and recognition conditions",
    "",
    "| Step | Class | Conditions | Marginal | Cumulative |",
    "|---:|---:|---|---:|---:|",
]
for case in learning_order:
    conditions = "; ".join(case["conditions"])
    flowchart_lines.append(
        f"| {case['step']} | {case['class']} | {conditions} | "
        f"{case['marginal_percentage']:.6f}% | {case['cumulative_percentage']:.6f}% |"
    )

if MAX_CONDITION_TERMS == 8:
    inspection_steps = [
        "1. Check the `d = c` and `U = C` edge–center branches and reuse matching relationships across orientations.",
        "2. Within `d = c`, check the direct equalities first, then reuse `C to D` for classes 26 and 29.",
        "3. Reuse `U to UL` for classes 22, 24, and 28. Only the parenthesized starting position changes.",
        "4. Check the adjacent-edge branch, then the two distances for class 31.",
        "5. The branches are not mutually exclusive; stop at any matching learned case.",
    ]
else:
    inspection_steps = [
        "1. Check the `d = c` and `U = C` edge–center branches. Their rotated forms are the same geometric kind of check, so reuse what you notice across orientations.",
        "2. Test a listed second condition only when its branch equality holds. This avoids doing the four-variable calculations for unrelated states.",
        "3. In the `d = c` branch, reuse `C to D` for both classes 26 and 29.",
        "4. Read the two `to` distances directly from the dials and compare them. Only classes 41 and 46 require a sum (`R + l` or `L + r`), calculated once around the clock face.",
        "5. Separately check the adjacent-edge branch. Classes 42 and 47 need a second equality; classes 32 and 33 compare two distances.",
        "6. Stop at any matching learned case; the branches are not mutually exclusive.",
    ]

flowchart_lines.extend([
    "",
    "## Inspection procedure",
    "",
    *inspection_steps,
    "",
])
(LEARNING_ORDER_DIR / "flowchart.md").write_text(
    "\n".join(flowchart_lines),
    encoding="utf-8",
)

print(f"{FLOWCHART_NAME} classes: {len(learning_order)}")
print(f"Eight-orientation coverage: {learning_result['coverage_percentage']:.6f}%")
print("Learning order:", " ".join(str(case["class"]) for case in learning_order))
print(f"Saved to {LEARNING_ORDER_DIR}")
