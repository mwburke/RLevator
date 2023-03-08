from rlevator.elevator import Elevator
from rlevator.passenger import Passenger

from copy import deepcopy


TEST_PASSENGERS = [
    Passenger(
        start_step=0,
        start_floor=0,
        destination_floor=5,
        max_wait_steps=50
    ),
    Passenger(
        start_step=0,
        start_floor=0,
        destination_floor=9,
        max_wait_steps=50
    ),
    Passenger(
        start_step=0,
        start_floor=0,
        destination_floor=2,
        max_wait_steps=50
    ),
    Passenger(
        start_step=0,
        start_floor=0,
        destination_floor=2,
        max_wait_steps=50
    )
]


TEST_ELEVATOR = Elevator(
    start_floor=0,
    capacity=10,
    min_floor=0,
    max_floor=10
)


def test_load_passengers_from_zero():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers)

    assert elevator.get_count_passengers() == 4


def test_load_passengers_multiple_load():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers_0 = deepcopy(TEST_PASSENGERS)
    passengers_1 = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers_0)
    elevator.load_passengers(passengers_1)

    assert elevator.get_count_passengers() == 8


def test_capacity():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers)

    assert elevator.available_capacity() == 6


def test_capacity_full():
    elevator = deepcopy(TEST_ELEVATOR)

    assert elevator.available_capacity() == 10


def test_empty_capacity():
    elevator = deepcopy(TEST_ELEVATOR)

    assert elevator.available_capacity() == elevator.get_capacity()


def test_destinations():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers)

    floors = elevator.destination_floors()

    assert floors == set([2, 5, 9])


def test_move():
    elevator = deepcopy(TEST_ELEVATOR)
    floor_diff = 1
    elevator.move(floor_diff)

    assert elevator.get_current_floor() == 1


def test_move_wait():
    elevator = deepcopy(TEST_ELEVATOR)
    floor_diff = 0
    elevator.move(floor_diff)

    assert elevator.get_current_floor() == 0


def test_move_out_of_bounds_min():
    elevator = Elevator(
        start_floor=5,
        capacity=10,
        min_floor=5,
        max_floor=10
    )

    floor_diff = -1
    elevator.move(floor_diff)

    assert elevator.get_current_floor() == 5


def test_move_out_of_bounds_top():
    elevator = Elevator(
        start_floor=10,
        capacity=10,
        min_floor=5,
        max_floor=10
    )

    floor_diff = 1
    elevator.move(floor_diff)

    assert elevator.get_current_floor() == 10


def test_unload_empty():
    elevator = Elevator(
        start_floor=10,
        capacity=10,
        min_floor=5,
        max_floor=10
    )

    passengers = elevator.unload_passengers()

    assert passengers == []


def test_unload_not_destination_floor():
    elevator = deepcopy(TEST_ELEVATOR)
    elevator.move(3)

    passengers = elevator.unload_passengers()

    assert passengers == []


def test_unload_destination_floor():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers)
    elevator.move(2)

    expected_passengers = elevator.passengers[2:4]

    passengers = elevator.unload_passengers()

    assert passengers == expected_passengers


def test_unload_destination_floor_remaining_count():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers)
    elevator.move(2)

    passengers = elevator.unload_passengers()

    assert elevator.get_count_passengers() == 2


def test_correct_move_counts():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers)
    elevator.move(4)

    # Act as if we just came from floor 3

    assert elevator.count_correct_move_passengers(3) == 2


def test_incorrect_move_counts():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers)
    elevator.move(4)

    # Act as if we just came from floor 3

    assert elevator.count_incorrect_move_passengers(3) == 2


def test_increment_passenger_steps_age():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers)

    elevator.increment_passenger_steps()

    match_count = 0
    for passenger in elevator.passengers:
        if passenger.get_age() == 1:
            match_count += 1

    assert match_count == 4


def test_increment_passenger_steps_wait():
    elevator = deepcopy(TEST_ELEVATOR)
    passengers = deepcopy(TEST_PASSENGERS)

    elevator.load_passengers(passengers)

    elevator.increment_passenger_steps()

    match_count = 0
    for passenger in elevator.passengers:
        if passenger.get_wait() == 0:
            match_count += 1

    assert match_count == 4
