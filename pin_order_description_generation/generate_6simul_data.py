from six_simul_data_dict import six_simul_data_dict, PinConfig, MemoConfig, IntuitivConfig, IntuitionFlags, DirectionBlocks, DirectionConfig
from memo_and_conditions import generate_memo_and_condition
from intuitive_or_not_and_blocks import generate_intuitiv_memo_blocks 

from itertools import permutations
import json
from dataclasses import asdict
import pickle

def gen_data(pin_order: list[str], include_memo=False, include_all_permutations_of_pin_order=False, filename: str | None=None, use_pickle=True) -> list[six_simul_data_dict]:
    """Generates a data dictionary that encompasses memo, conditions, intuitive and memorized moves and a description of which blocks the intuitive moves "assemble".
    Set include_memo=True to also generate memo and conditions for the pin_set.
    Set a filename to save to disk. Will store in either json format or as a pickle file (if use_pickle == True).
    """

    memo = None
    conditions = None
    if include_memo:
        memo, conditions = generate_memo_and_condition(pin_order)

    # Either iterate over all permutations of the pin_order, or just the one the user gave us
    if include_all_permutations_of_pin_order:
        pin_orders = [list(p) for p in permutations(pin_order)]
    else:
        pin_orders = [pin_order]

    result = [] 
    for order in pin_orders:
        intuition_result = generate_intuitiv_memo_blocks(order)
    
        # init data dict
        d = six_simul_data_dict(
            pins = [
                PinConfig(
                    pin_code=order[i],
                    memo=MemoConfig(up="", down=""),
                    intuitiv=IntuitivConfig(
                        up_to_down=DirectionConfig(
                            intuition=IntuitionFlags(up=None, down=None),
                            blocks=DirectionBlocks(up=[], down=[]),
                        ),
                        down_to_up=DirectionConfig(
                            intuition=IntuitionFlags(up=None, down=None),
                            blocks=DirectionBlocks(up=[], down=[]),
                        ),
                    ),
                )
                for i in range(len(order))
            ],
            conditions=conditions,
        )

        # Populate memo
        if memo:
            for i in range(len(d.pins)):
                pin_config = d.pins[i]
                
                pin_memo = next(
                    (d for d in memo if pin_config.pin_code in d),
                    None,  # default if not found
                )

                assert pin_memo, f"{pin_memo} was not found in memo"

                pin_config.memo.up = pin_memo[pin_config.pin_code]["up"]
                pin_config.memo.down = pin_memo[pin_config.pin_code]["down"]
        
        # Populate intuitiv/memo and blocks
        for i, r in enumerate(intuition_result):
            pin_config = d.pins[i]
            assert pin_config.pin_code in r

            intuitive_memo_data = r[pin_config.pin_code]
            
            pin_config.intuitiv.up_to_down.intuition.up = intuitive_memo_data["up_then_down"][0][0]
            pin_config.intuitiv.up_to_down.intuition.down = intuitive_memo_data["up_then_down"][0][1]
            pin_config.intuitiv.up_to_down.blocks.up = intuitive_memo_data["up_then_down"][1][0]
            pin_config.intuitiv.up_to_down.blocks.down = intuitive_memo_data["up_then_down"][1][1]

            pin_config.intuitiv.down_to_up.intuition.up = intuitive_memo_data["down_then_up"][0][0]
            pin_config.intuitiv.down_to_up.intuition.down = intuitive_memo_data["down_then_up"][0][1]
            pin_config.intuitiv.down_to_up.blocks.up = intuitive_memo_data["down_then_up"][1][0]
            pin_config.intuitiv.down_to_up.blocks.down = intuitive_memo_data["down_then_up"][1][1]

        result.append(d) 

    if filename is not None:
        if use_pickle:
            with open(filename, "wb") as f:
                pickle.dump(result, f)
        else:
            serializable = [asdict(item) for item in result]
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(serializable, f, ensure_ascii=False, default=str, indent=2)

    return result

if __name__ == "__main__":
    # Usage:
    filename="ur_UL_\\_DR_R_UR"

    pin_order = ["ur", 'UL', '\\', 'DR', 'R', 'UR']

    # to gen and save to json
    # gen_data(pin_order, include_memo=True, include_all_permutations_of_pin_order=True, filename=f"{filename}.json", use_pickle=False)

    # gen and save as pickle
    gen_data(pin_order, include_memo=True, include_all_permutations_of_pin_order=True, filename=f"{filename}.pkl", use_pickle=True)

    # To read the json data again:
    """
    import json

    with open(f"{filename}.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print(data)
    """

    # To read the pickle dump:
    """
    with open(f"{filename}.pkl", "rb") as f:
        loaded_result = pickle.load(f)
        print(loaded_result)
    """

