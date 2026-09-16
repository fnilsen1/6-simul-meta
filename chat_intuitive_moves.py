from itertools import permutations

# Universe
U = set(range(1, 10))   # {1, 2, ..., 9}

# Define pins: name -> (A, B)
pins = {
    "UL": ({1, 2, 4, 5}, {3, 7, 9}),
    'UR': ({2,3,5,6}, {1,7,9}),
    'DR': ({5,6,8,9}, {1,3,7}),
    "DL": ({4, 5, 7, 8}, {1, 3, 9}),
    'U': ({1,2,3,4,5,6}, {7,9}),
    "\\": ({1, 2, 4, 5, 6, 8, 9}, {3, 7}),
    'L': ({1,2,4,5,7,8}, {3, 9}),
    "R": ({2, 3, 5, 6, 8, 9}, {1, 7}),
    '/': ({2,3,4,5,6,7,8}, {1,9}),
    'D': ({4,5,6,7,8,9}, {1,3}),
    'dl': ({1,2,3,4,5,6,8,9}, {7}),
    "dr": ({1, 2, 3, 4, 5, 6, 7, 8}, {9}),
    "ur": ({1, 2, 4, 5, 6, 7, 8, 9}, {3}),
    'ul': ({2,3,4,5,6,7,8,9}, {1}),
    "ALL": ({1,2,3,4,5,6,7,8,9}, {}),
    'all': ({}, {1, 3, 7, 9}),
}


def print_partition(partition):
    """Pretty-print a partition like {{1,2}, {3}, {4,5}}."""
    blocks_str = []
    for block in partition:
        blocks_str.append("{" + ",".join(str(x) for x in sorted(block)) + "}")
    print("{" + ", ".join(blocks_str) + "}")


def refine_by_set(partition, S):
    """
    Apply one trekk S to the partition:
    each block C becomes up to two blocks: C∩S and C\S (empty discarded).
    Returns (new_partition, split_happened).
    """
    new_partition = []
    split_happened = False

    for C in partition:
        C_in = C & S
        C_out = C - S

        pieces = [p for p in (C_in, C_out) if p]
        if len(pieces) > 1:
            split_happened = True

        new_partition.extend(pieces)

    return new_partition, split_happened


def run_for_order(pin_order):
    """
    Run one specific order of pins.
    Returns:
      chain: list of (A_status, B_status) for each pin
      intuitive_count: total number of "I" trekk
      memo_count:      total number of "M" trekk
    First pin is forced to (I,I) ad hoc.
    """

    pin_order = pin_order[::-1]
    partition = [U]
    chain = []
    intuitive_count = 0
    memo_count = 0

    for idx, name in enumerate(pin_order):
        A, B = pins[name]

        # Step 1: apply A
        partition, split_A = refine_by_set(partition, A)
        A_status = "I" if split_A else "M"

        # Step 2: apply B on the updated partition
        partition, split_B = refine_by_set(partition, B)
        B_status = "I" if split_B else "M"

        # Ad hoc: force the first pin to (I, I)
        if idx == 0:
            A_status = "I"
            B_status = "I"

        chain.append((A_status, B_status))

        # Count these two trekk
        for s in (A_status, B_status):
            if s == "I":
                intuitive_count += 1
            else:
                memo_count += 1

    return chain, intuitive_count, memo_count


def run_and_show(pin_order):
    """
    Run one specific order of pins and *print* everything:
      - starting partition,
      - partition after each pin,
      - (A,B) statuses per pin,
      - final chain and counts.
    """
    pin_order = pin_order[::-1]
    partition = [U]
    chain = []
    intuitive_count = 0
    memo_count = 0

    # print("Chosen order:", pin_order)
    print("Start partition:")
    print_partition(partition)
    print("-" * 40)

    for idx, name in enumerate(pin_order):
        A, B = pins[name]

        partition, split_A = refine_by_set(partition, A)
        A_status = "I" if split_A else "M"

        partition, split_B = refine_by_set(partition, B)
        B_status = "I" if split_B else "M"

        if idx == 0:
            A_status = "I"
            B_status = "I"

        chain.append((A_status, B_status))

        for s in (A_status, B_status):
            if s == "I":
                intuitive_count += 1
            else:
                memo_count += 1

        print(f'After P("{name}")  (A={A_status}, B={B_status}):')
        print_partition(partition)
        print("-" * 40)

    chain_str = " -> ".join(f"({a},{b})" for (a, b) in chain)
    print("Chain of (A,B):")
    print(chain_str)
    print(f"Total I: {intuitive_count}, total M: {memo_count}")


def run_all_permutations(base_order):
    """
    Loop over all permutations of base_order.
    For each permutation, print:
      - permutation itself,
      - chain of (A,B),
      - total I and M.
    """
    for perm in permutations(base_order):
        chain, intuitive, memo = run_for_order(list(perm))
        chain_str = " -> ".join(f"({a},{b})" for (a, b) in chain)

        print("Permutation:", perm)
        print("Chain:", chain_str)
        print(f"Total I: {intuitive}, total M: {memo}")
        print("-" * 40)

# note to self: ikke stol på kajrakso. reverser
def main():
    # from itertools import combinations
    # orders = combinations(list(pins.keys())[:-2], 6)
    # for order in orders:
    #     order = list(order)
    #     # base_order = ["\\", "ur", "UL", "R", "dr", "DL"]
    #
    #     # 1) Inspect one specific order in detail:
    #     run_and_show(order)
    #
    #     print("\n===== ALL PERMUTATIONS =====\n")
    #
    #     # 2) Inspect all permutations (only chains & counts):
    #     run_all_permutations(order)
    #

    # order = ['dl', 'U', 'UL', 'UR', 'DR', 'DL']
    order = ["ur","L","UL","\\","DR","UR"]
    order = ["ur","UL","\\","DR","R","UR"]

    #     # 2) Inspect all permutations (only chains & counts):
    # run_all_permutations(order)
    # Chain: (I,I) -> (I,I) -> (I,I) -> (I,I) -> (I,M) -> (M,M)
    # Total I: 9, total M: 3
    run_and_show(order)

    chain, intuitive_moves, memo_moves = run_for_order(order)

    print(intuitive_moves) 




if __name__ == "__main__":
    main()

