FOUR_VARIABLE_DIR = OUTPUT_DIR / "4_total_variables_learning_order"
FOUR_VARIABLE_DIR.mkdir(exist_ok=True)


def condition_variable_count(row):
    """Count nonzero variable terms; coefficients such as 2u count once."""
    return int(np.count_nonzero(np.asarray(row) % 12))


saved_best_cases = json.loads(
    (OUTPUT_DIR / "6_simul_best_pin_orders.json").read_text(encoding="utf-8")
)["classes"]
best_case_by_number = {case["class"]: case for case in saved_best_cases}

four_variable_cases = []
for class_data in classes:
    best_case = best_case_by_number[class_data["class"]]
    best_pin_set = tuple(sorted(best_case["best_pin_order"], key=pin_order.get))
    displayed_basis = condition_bases[best_pin_set]
    first_count, second_count = [
        condition_variable_count(row) for row in displayed_basis
    ]
    if first_count + second_count == 4:
        four_variable_cases.append({
            "class": class_data["class"],
            "best_pin_order": best_case["best_pin_order"],
            "conditions": list(best_case["conditions"]),
            "condition_variable_counts": [first_count, second_count],
            "total_condition_variables": 4,
            "d_moves": best_case["d_moves"],
            "transitions": best_case["transitions"],
            "intuitive_moves": best_case["intuitive_moves"],
            "standalone_percentage": best_case["scrambles_solved_percentage"],
            "representative": tuple(class_data["pin_sets"][0]),
        })

assert len(four_variable_cases) == 13

# Build each class's union over all eight orientations.
system_by_signature = {}
case_signatures = []
for case in four_variable_cases:
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
solved_by_case = np.empty((len(four_variable_cases), sample_count), dtype=bool)

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
remaining = set(range(len(four_variable_cases)))
learning_order = []
while remaining:
    choice = max(
        remaining,
        key=lambda index: (
            np.count_nonzero(solved_by_case[index] & ~covered),
            -four_variable_cases[index]["d_moves"],
            -four_variable_cases[index]["transitions"],
            four_variable_cases[index]["intuitive_moves"],
            -four_variable_cases[index]["class"],
        ),
    )
    new_states = solved_by_case[choice] & ~covered
    covered |= solved_by_case[choice]
    remaining.remove(choice)

    case = dict(four_variable_cases[choice])
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
    "description": "Greedy marginal-coverage order for classes with four total condition variables",
    "all_eight_orientations": True,
    "coverage_method": "2,000,000 uniformly sampled states; overlaps counted once",
    "condition_complexity_definition": "sum of nonzero variable terms across both equations; coefficients count once",
    "class_count": len(learning_order),
    "coverage_percentage": learning_order[-1]["cumulative_percentage"],
    "classes": learning_order,
}
(FOUR_VARIABLE_DIR / "learning_order.json").write_text(
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

(FOUR_VARIABLE_DIR / "orientation_lookup.json").write_text(
    json.dumps({"classes": orientation_lookup}, indent=2) + "\n",
    encoding="utf-8",
)

flowchart_lines = [
    "# Four-total-variable inspection flowchart",
    "",
    f"Estimated coverage across all eight orientations: {learning_result['coverage_percentage']:.6f}%.",
    "",
    "Every learned case is only two equality checks. Do not run a separate full flowchart for each angle: record equal dial groups once, then match those pairs against `orientation_lookup.json`.",
    "",
    "```text",
    "START",
    "│",
    "├─ d = c branch",
    "│  ├─ d = r ───────────────────── Class 1",
    "│  ├─ d = u ───────────────────── Class 2",
    "│  ├─ r = u ───────────────────── Class 3",
    "│  ├─ l = u ───────────────────── Class 4",
    "│  └─ C = D ───────────────────── Class 8",
    "│",
    "├─ U = C branch",
    "│  ├─ r = c ───────────────────── Class 10",
    "│  ├─ r = u ───────────────────── Class 11",
    "│  ├─ l = u ───────────────────── Class 13",
    "│  ├─ c = l ───────────────────── Class 14",
    "│  ├─ d = r ───────────────────── Class 25",
    "│  └─ d = l ───────────────────── Class 30",
    "│",
    "└─ Two matching adjacent-edge pairs",
    "   ├─ L = D and r = u ─────────── Class 42",
    "   └─ U = L and d = r ─────────── Class 47",
    "```",
    "",
    "## Learning order and canonical conditions",
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

flowchart_lines.extend([
    "",
    "## Inspection procedure",
    "",
    "1. Check the `d = c` and `U = C` edge–center branches. Their rotated forms are the same geometric kind of check, so reuse what you notice across orientations.",
    "2. Test the listed second equality only when its branch equality holds.",
    "3. Separately check the two adjacent-edge-pair patterns for classes 42 and 47.",
    "4. Stop at any matching learned case; the branches are not mutually exclusive.",
    "",
])
(FOUR_VARIABLE_DIR / "flowchart.md").write_text(
    "\n".join(flowchart_lines),
    encoding="utf-8",
)

print(f"Four-variable classes: {len(learning_order)}")
print(f"Eight-orientation coverage: {learning_result['coverage_percentage']:.6f}%")
print("Learning order:", " ".join(str(case["class"]) for case in learning_order))
print(f"Saved to {FOUR_VARIABLE_DIR}")
