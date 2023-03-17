from rlevator.building import Building
from rlevator.passenger import Passenger
from rlevator.actions import Action

from copy import deepcopy


BUILDING_0 = Building(
    num_floors=10,
    num_elevators=2,
    max_queue=20,
    elevator_capacities=10,
    elevator_start_floors=None,
    elevator_bounds=None
)

BUILDING_1 = Building(
    num_floors=10,
    num_elevators=2,
    max_queue=20,
    elevator_capacities=10,
    elevator_start_floors=[1, 2],
    elevator_bounds=[[0, 9], [0, 8]]
)


BUILDING_2 = deepcopy(BUILDING_0)

PASSENGERS_0 = [
    Passenger(0, 0, 1),
    Passenger(0, 1, 0),
    Passenger(0, 5, 9),
    Passenger(0, 5, 8),
    Passenger(0, 5, 0),
]

BUILDING_2.add_arrivals_to_queues(PASSENGERS_0)


BUILDING_3 = Building(
    num_floors=3,
    num_elevators=2,
    max_queue=5,
    elevator_capacities=3,
    elevator_start_floors=None,
    elevator_bounds=None
)


PASSENGERS_1 = [
    Passenger(0, 0, 1),
    Passenger(0, 1, 0),
    Passenger(0, 1, 2)
]


BUILDING_3.add_arrivals_to_queues(PASSENGERS_1)


def test_elevators_exist():
    assert len(BUILDING_0.elevators) == 2


def test_elevators_start_floors_default():
    match_count = 0
    for elevator in BUILDING_0.elevators:
        if elevator.floor == 0:
            match_count += 1

    assert match_count == 2


def test_elevators_start_floors_non_default_0():
    assert BUILDING_1.elevators[0].get_current_floor() == 1


def test_elevators_start_floors_non_default_1():
    assert BUILDING_1.elevators[1].get_current_floor() == 2


def test_elevators_bounds_default_bottom():
    assert BUILDING_0.elevators[0].get_min_floor() == 0


def test_elevators_bounds_default_top():
    assert BUILDING_0.elevators[0].get_max_floor() == 9


def test_elevators_bounds_non_default_bottom():
    assert BUILDING_1.elevators[1].get_min_floor() == 0


def test_elevators_bounds_non_default_top():
    assert BUILDING_1.elevators[1].get_max_floor() == 8


def test_add_passengers_queues_0():
    assert len(BUILDING_2.get_queue(2)) == 0


def test_add_passengers_queues_1():
    assert len(BUILDING_2.get_queue(0, True)) == 1


def test_add_passengers_queues_2():
    assert len(BUILDING_2.get_queue(5, True)) == 2


def test_add_passengers_queues_3():
    assert len(BUILDING_2.get_queue(5, False)) == 1


def test_queue_request_buttons_statuses():
    building_statuses = BUILDING_3.queue_request_button_statuses()

    correct_building_statuses = [
        [True, True, False],
        [False, True, False]
    ]

    assert building_statuses == correct_building_statuses


def test_excess_passengers_max_queue():
    building = deepcopy(BUILDING_3)

    # Already has one in floor zero up queue with max queue of 5
    new_passengers = []
    for _ in range(6):
        new_passengers.append(Passenger(0, 0, 2))

    building.add_arrivals_to_queues(new_passengers)

    assert len(building.get_queue(0, True)) == building.max_queue


def test_excess_passengers_rejected_queue():
    building = deepcopy(BUILDING_3)

    # Already has one in floor zero up queue with max queue of 5
    new_passengers = []
    for _ in range(6):
        new_passengers.append(Passenger(0, 0, 2))

    building.add_arrivals_to_queues(new_passengers)

    assert len(building.get_rejected_queue_passengers()) == 2


def test_move_up():
    building = deepcopy(BUILDING_1)
    building.execute_action(1,  Action.MOVE_UP)

    assert building.elevators[1].floor == 3


def test_move_down():
    building = deepcopy(BUILDING_1)
    building.execute_action(1,  Action.MOVE_DOWN)

    assert building.elevators[1].floor == 1


def test_wait():
    building = deepcopy(BUILDING_1)
    building.execute_action(1,  Action.WAIT)

    assert building.elevators[1].floor == 2


def test_load_up_all():
    building = deepcopy(BUILDING_3)
    building.execute_action(0, Action.LOAD_UP)

    has_empty_queue = len(building.get_queue(0)) == 0
    has_one_passenger = building.elevators[0].get_count_passengers() == 1

    assert (has_empty_queue & has_one_passenger) is True


def test_load_up_remaining():
    building = deepcopy(BUILDING_3)

    load_passengers = []
    for _ in range(4):
        load_passengers.append(Passenger(0, 0, 2))

    building.add_arrivals_to_queues(load_passengers)

    building.execute_action(0, Action.LOAD_UP)

    has_correct_queue_length = len(building.get_queue(0, True)) == 2
    has_elevator_passengers = building.elevators[0].get_count_passengers() == 3

    assert (has_correct_queue_length & has_elevator_passengers) is True


def test_load_unload_count_unloaded():
    building = deepcopy(BUILDING_3)

    load_passengers = []
    for _ in range(4):
        load_passengers.append(Passenger(0, 0, 2))

    building.add_arrivals_to_queues(load_passengers)

    building.execute_action(0, Action.LOAD_UP)
    building.execute_action(0, Action.MOVE_UP)
    building.execute_action(0, Action.MOVE_UP)

    building.execute_action(0, Action.UNLOAD)

    assert len(building.get_deboarding_passengers()) == 2


def test_load_unload_count_elevator():
    building = deepcopy(BUILDING_3)

    load_passengers = []
    for _ in range(4):
        load_passengers.append(Passenger(0, 0, 2))

    building.add_arrivals_to_queues(load_passengers)

    building.execute_action(0, Action.LOAD_UP)
    building.execute_action(0, Action.MOVE_UP)
    building.execute_action(0, Action.MOVE_UP)

    building.execute_action(0, Action.UNLOAD)

    assert building.elevators[0].get_count_passengers() == 1


def test_increment_age():
    building = deepcopy(BUILDING_3)

    building.execute_action(0, Action.LOAD_UP)

    building._increment_step()

    meets_criteria = True

    for passenger in building.get_queue(1, True):
        meets_criteria &= passenger.get_age() == 1

    for passenger in building.get_queue(1, False):
        meets_criteria &= passenger.get_age() == 1

    for passenger in building.elevators[0].passengers:
        meets_criteria &= passenger.get_age() == 1

    assert meets_criteria is True


def test_increment_wait():
    building = deepcopy(BUILDING_3)

    building.execute_action(0, Action.LOAD_UP)

    building._increment_step()

    meets_criteria = True

    for passenger in building.get_queue(1, True):
        meets_criteria &= passenger.get_wait() == 1

    for passenger in building.get_queue(1, False):
        meets_criteria &= passenger.get_wait() == 1

    for passenger in building.elevators[0].passengers:
        meets_criteria &= passenger.get_wait() == 0

    assert meets_criteria is True


def test_max_wait_removal():
    building = deepcopy(BUILDING_3)

    max_wait_passengers = [
        Passenger(0, 0, 1),
        Passenger(0, 1, 0),
        Passenger(0, 1, 2)
    ]

    for passenger in max_wait_passengers:
        passenger.steps_age = 51
        passenger.steps_wait = 51

    building.add_arrivals_to_queues(max_wait_passengers)

    building.remove_max_wait_passengers()

    passenger_count = 0
    for queue in building.up_queues:
        passenger_count += len(queue)

    for queue in building.down_queues:
        passenger_count += len(queue)

    assert passenger_count == 3


def test_max_wait_removal_queue():
    building = deepcopy(BUILDING_3)

    max_wait_passengers = [
        Passenger(0, 0, 1),
        Passenger(0, 1, 0),
        Passenger(0, 1, 2)
    ]

    for passenger in max_wait_passengers:
        passenger.steps_age = 51
        passenger.steps_wait = 51

    building.add_arrivals_to_queues(max_wait_passengers)

    building.remove_max_wait_passengers()

    passenger_count = 0
    for queue in building.up_queues:
        passenger_count += len(queue)

    for queue in building.down_queues:
        passenger_count += len(queue)

    assert len(building.reached_max_wait_passengers) == 3
