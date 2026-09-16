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
    each block C becomes up to two blocks: C∩S and C\\S (empty discarded).
    Returns (new_partition, split_happened).
    """
    new_partition = []
    split_happened = False

    for C in partition:
        C_in = C & S
        C_out = C - S

        pieces = [frozenset(p) for p in (C_in, C_out) if p]
        if len(pieces) > 1:
            split_happened = True

        new_partition.extend(pieces)

    return set(new_partition), split_happened


def to_list_of_set(x: set[frozenset]):
    return [set(_x) for _x in x]

def run(pin_order):
    """
    Run one specific order of pins and *print* everything:
      - starting partition,
      - partition after each pin,
      - (A,B) statuses per pin,
      - final chain and counts.
    """
    partition: set | list = set([frozenset(U)])
    partitions = [[((partition), (partition)), ((partition), (partition))]]
    statuses = []

    chain = []
    intuitive_count = 0
    memo_count = 0

    # we need to reverse pin_order since
    # we analyse the chain "up side down"
    pin_order = pin_order[::-1]

    for idx, name in enumerate(pin_order):
        # hvorfor kalte chat det for A og B????
        # det er UP pins og DOWN pins
        A, B = pins[name]

        # U og så D (dette er forvirrende...)
        partition_UD_B, split_B = refine_by_set(partition, B)
        B_status_UD = "I" if split_B else "M"

        partition_UD_A, split_A = refine_by_set(partition_UD_B, A)
        A_status_UD = "I" if split_A else "M"

        # D og så U (dette er forvirrende...)
        partition_DU_A, split_A = refine_by_set(partition, A)
        A_status = "I" if split_A else "M"

        partition_DU_B, split_B = refine_by_set(partition_DU_A, B)
        B_status = "I" if split_B else "M"

        assert partition_DU_B == partition_UD_A
        partition = partition_DU_B

        statuses.append([(A_status_UD, B_status_UD), (A_status, B_status)])
        partitions.append([(partition_UD_A, partition_UD_B), (partition_DU_A, partition_DU_B)])

        if idx == 0:
            A_status = "I"
            B_status = "I"

        chain.append((A_status, B_status))

        for s in (A_status, B_status):
            if s == "I":
                intuitive_count += 1
            else:
                memo_count += 1

    # reverse these since this function solves "bottom up"
    return partitions[::-1], statuses[::-1]


def generate_intuitiv_memo_blocks(pin_order: list[str]):
    parts, statuses = run(pin_order)

    intuitive = []
    for i in range(len(parts) - 1):
        
        # need to produce one list of two tuples:
        # up_to_down, down_to_up
        # [(),         ()]     
        # where each tuple is
        # (block made by U move, block made by D move)
    
        up_then_down_i = parts[i][0]
        down_then_up_i = parts[i][1]
        up_then_down_ip = parts[i+1][0]
        down_then_up_ip = parts[i+1][1]

        # if pin_order[i] == 'R':
        #     print(parts[i])
        #     print(parts[i+1])

        # up_then_down

        # up
        up_then_down_up = up_then_down_i[1] - up_then_down_i[0]

        # down
        up_then_down_down = up_then_down_ip[0] - up_then_down_i[1]

        # down_then_up
        # up
        down_then_up_up = down_then_up_ip[1] - down_then_up_i[0]

        # down
        down_then_up_down = down_then_up_i[0] - down_then_up_i[1]

        intuitive.append({
                "up_then_down": (up_then_down_up, up_then_down_down),
                "down_then_up": (down_then_up_up, down_then_up_down)
        })

    # Prettify. convert frozensets
    intuitive_pretty = []
    for intu in intuitive:
        intuitive_pretty.append({
            "up_then_down": ([set(x) for x in list(intu["up_then_down"][0])], [set(x) for x in list(intu["up_then_down"][1])]),
            "down_then_up": ([set(x) for x in list(intu["down_then_up"][0])], [set(x) for x in list(intu["down_then_up"][1])]),
        })

    results = [] 
    for i, intui in enumerate(intuitive_pretty):
        results.append({
            pin_order[i]: {
                "up_then_down": (statuses[i][0], intui["up_then_down"]),
                "down_then_up": (statuses[i][1], intui["down_then_up"]),
            }
        })

    return results

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

    order = ["ur", 'UL', '\\', 'DR', 'R', 'UR']

    r = generate_intuitiv_memo_blocks(order)
    for _r in r:
        print(_r)




if __name__ == "__main__":
    main()

