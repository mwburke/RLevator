from enum import Enum


class Action(Enum):
    """
    There are 6 actions that an elevator can take:
    1. Attempt to move up a floor. This does nothing if at the
       elevator's maximum floor.
    2. Attempt to move down a floor. This does nothing if at the
       elevator's minimum floor.
    3. Do nothing and remain at the current floor.
    4. Load as many passengers will fit in the remaining elevator
       capacity from the current floor that are in the up queue
       starting from the first arrived passengers onward.
    5. Load as many passengers will fit in the remaining elevator
       capacity from the current floor that are in the down queue
       starting from the first arrived passengers onward.
    6. Unload any passengers that have their destination floor as
       the elevator's current floor.
    """
    MOVE_UP = 1
    MOVE_DOWN = 2
    WAIT = 3
    LOAD_UP = 4
    LOAD_DOWN = 5
    UNLOAD = 6


NUM_TO_ACTION = {
    1: Action.MOVE_UP,
    2: Action.MOVE_DOWN,
    3: Action.WAIT,
    4: Action.LOAD_UP,
    5: Action.LOAD_DOWN,
    6: Action.UNLOAD
}
