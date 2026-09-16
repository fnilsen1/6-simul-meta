from six_simul_data_dict import six_simul_data_dict, PinConfig, MemoConfig, IntuitivConfig, IntuitionFlags, DirectionBlocks, DirectionConfig
from memo_and_conditions import generate_memo_and_condition
from intuitive_or_not_and_blocks import generate_intuitiv_memo_blocks 

def gen_data(pin_order: list[str], include_memo=False) -> six_simul_data_dict:
    """Generates a data dictionary that encompasses memo, conditions, intuitive and memorized moves and a description of which blocks the intuitive moves "assemble".
    Set include_memo=True to also generate memo and conditions for the pin_set."""

    # todo: the memo and condition is not dependent on the order, so this
    # should only be computed once per "pin set".
    memo = None
    conditions = None
    if include_memo:
        memo, conditions = generate_memo_and_condition(pin_order)
    intuition_result = generate_intuitiv_memo_blocks(pin_order)
    
    # init data dict
    d = six_simul_data_dict(
        pins = [
            PinConfig(
                pin_code=pin_order[i],
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
            for i in range(len(pin_order))
        ],
        conditions=conditions,
    )

    # Populate memo
    if memo:
        for i, pin_memo in enumerate(memo):
            pin_config = d.pins[i]
            assert pin_config.pin_code in pin_memo


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
    
    return d

if __name__ == "__main__":
    # Usage:
    pin_order = ["ur", 'UL', '\\', 'DR', 'R', 'UR']
    d = gen_data(pin_order, include_memo=False)
    print(d)
