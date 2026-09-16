from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

number_to_notation = {
    1: "UL",
    2: "U",
    3: "UR",
    4: "L",
    5: "C",
    6: "R",
    7: "DL",
    8: "D",
    9: "DR",
}

# -------------------------------------------------------------------
# 1. Basic types
# -------------------------------------------------------------------

@dataclass
class IntuitionFlags:
    """
    Intuition flags for a direction.
    You can keep using "I"/"M"/etc. or change to bools if you prefer.
    """
    up: str | None      # e.g. "I", "M"
    down: str | None    # e.g. "I", "M"


@dataclass
class DirectionBlocks:
    """
    Blocks produced for a given direction.

    'up' and 'down' are lists of blocks.
    Each block is a list of ints, e.g. [1, 2, 3].
    """
    up: List[List[int]] = field(default_factory=list)
    down: List[List[int]] = field(default_factory=list)


@dataclass
class DirectionConfig:
    """
    Configuration for a specific direction change:
    UP -> DOWN or DOWN -> UP.
    """
    intuition: IntuitionFlags
    blocks: DirectionBlocks


@dataclass
class IntuitivConfig:
    """
    Full "intuitiv" configuration for a pin:
    both directions: UP -> DOWN and DOWN -> UP.
    """
    up_to_down: DirectionConfig
    down_to_up: DirectionConfig


@dataclass
class MemoConfig:
    """
    Memo strings for UP and DOWN.
    """
    up: str
    down: str


@dataclass
class PinConfig:
    """
    All data for a single pin.
    """
    pin_code: str          # "", "ur", "L", etc.
    memo: MemoConfig
    intuitiv: IntuitivConfig

@dataclass
class six_simul_data_dict:
    """Contains a pin order, memo for each pin position, conditions etc. ."""
    pins: List[PinConfig] = field(default_factory=list)
    conditions: list[str] | None = field(default_factory=list)
    

    def __str__(self):
        s = ""
        s += f"Conditions: {self.conditions}\n"
        s += f"Pin order:\n"
        for pin_nummer in range(len(self.pins)):
            pin = self.pins[pin_nummer]
            
            s += f"{pin.pin_code}\n"
            s += f"\tMemo UP: {pin.memo.up}\n"
            s += f"\tMemo DOWN: {pin.memo.down}\n"

            up_to_down_blocks_up = [
               " ".join([number_to_notation[y] for y in x]) for x in pin.intuitiv.up_to_down.blocks.up
            ]
            up_to_down_blocks_down = [
                " ".join([number_to_notation[y] for y in x]) for x in pin.intuitiv.up_to_down.blocks.down
            ]
            down_to_up_blocks_up = [
                " ".join([number_to_notation[y] for y in x]) for x in pin.intuitiv.down_to_up.blocks.up
            ]
            down_to_up_blocks_down = [
                " ".join([number_to_notation[y] for y in x]) for x in pin.intuitiv.down_to_up.blocks.down
            ]

            down_to_up_str_up = f"UP ({pin.intuitiv.down_to_up.intuition.up}) {down_to_up_blocks_up}"
            down_to_up_str_down = f"DOWN ({pin.intuitiv.down_to_up.intuition.down}) {down_to_up_blocks_down}"
            up_to_down_str_up = f"UP ({pin.intuitiv.up_to_down.intuition.up}) {up_to_down_blocks_up}"
            up_to_down_str_down = f"DOWN ({pin.intuitiv.up_to_down.intuition.down}) {up_to_down_blocks_down}"

            s += f"\t{up_to_down_str_up:<20} -> {up_to_down_str_down:<20}\n"
            s += f"\t{down_to_up_str_down:<20} -> {down_to_up_str_up:<20}\n"
            s += "\n"

        return s

# -------------------------------------------------------------------
# 2. Example construction
#    (You can remove this once you start generating real data.)
# -------------------------------------------------------------------

def make_example_scheme() -> six_simul_data_dict:
    # Example pin 1 (your original "ur" example)
    pin1 = PinConfig(
        pin_code="ur",
        memo=MemoConfig(
            up="u - U + L - UR",
            down="L - U + u",
        ),
        intuitiv=IntuitivConfig(
            up_to_down=DirectionConfig(
                intuition=IntuitionFlags(up="I", down="M"),
                blocks=DirectionBlocks(
                    up=[[1, 2, 3]],
                    down=[],
                ),
            ),
            down_to_up=DirectionConfig(
                intuition=IntuitionFlags(up="I", down="M"),
                blocks=DirectionBlocks(
                    up=[],
                    down=[],
                ),
            ),
        ),
    )

    # Example pin 2 (your "L" example)
    pin2 = PinConfig(
        pin_code="L",
        memo=MemoConfig(
            up="u - R - UR",
            down="c-d",
        ),
        intuitiv=IntuitivConfig(
            up_to_down=DirectionConfig(
                intuition=IntuitionFlags(up="I", down="I"),
                blocks=DirectionBlocks(
                    up=[[7, 9], [2, 3]],
                    down=[],
                ),
            ),
            down_to_up=DirectionConfig(
                intuition=IntuitionFlags(up="I", down="I"),
                blocks=DirectionBlocks(
                    up=[],
                    down=[[1, 2]],
                ),
            ),
        ),
    )

    id_scheme = six_simul_data_dict(
        pins=[
            # You can add an "empty" pin 0 if needed:
            PinConfig(
                pin_code="",
                memo=MemoConfig(up="", down=""),
                intuitiv=IntuitivConfig(
                    up_to_down=DirectionConfig(
                        intuition=IntuitionFlags(up="I", down="I"),
                        blocks=DirectionBlocks(),
                    ),
                    down_to_up=DirectionConfig(
                        intuition=IntuitionFlags(up="I", down="I"),
                        blocks=DirectionBlocks(),
                    ),
                ),
            ),
            pin1,
            pin2,
            # ... add pins 3, 4, 5, etc.
        ]
    )

    return id_scheme


# -------------------------------------------------------------------
# 3. Example usage
# -------------------------------------------------------------------

if __name__ == "__main__":
    scheme = make_example_scheme()
    print(scheme)

