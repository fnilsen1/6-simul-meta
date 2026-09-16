_learning_order_config = {
    "max_condition_terms": 8,
    "count_coefficient_repetitions": False,
    "expected_class_count": 24,
    "folder_name": "8_total_variables_learning_order",
    "flowchart_name": "Maximum-eight-term",
}

try:
    exec(
        Path("six_variable_learning_order.py").read_text(encoding="utf-8"),
        globals(),
    )
finally:
    del _learning_order_config
