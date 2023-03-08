from rlevator.passenger import Passenger

from copy import deepcopy


# Create test passengers
PASSENGER_0 = Passenger(
    start_step=0,
    start_floor=0,
    destination_floor=5,
    max_wait_steps=50
)


def test_reached_destination_negative():
    assert PASSENGER_0.reached_destination(1) is False


def test_reached_destination_positive():
    assert PASSENGER_0.reached_destination(5) is True


def test_age():
    passenger = deepcopy(PASSENGER_0)

    in_elevator = False

    num_steps = 51

    for _ in range(num_steps):
        passenger.increment_step(in_elevator)

    assert passenger.get_age() == 51


def test_wait():
    passenger = deepcopy(PASSENGER_0)

    in_elevator = False

    num_steps = 51

    for _ in range(num_steps):
        passenger.increment_step(in_elevator)

    assert passenger.get_wait() == 51


def test_wait_elevator_no_increment():
    passenger = deepcopy(PASSENGER_0)

    in_elevator = False

    num_steps = 20

    for _ in range(num_steps):
        passenger.increment_step(in_elevator)

    in_elevator = True

    num_steps = 20

    for _ in range(num_steps):
        passenger.increment_step(in_elevator)

    assert passenger.get_wait() == 20


def test_reached_max_wait_negative():
    passenger = deepcopy(PASSENGER_0)

    in_elevator = False

    num_steps = 49

    for _ in range(num_steps):
        passenger.increment_step(in_elevator)

    assert passenger.reached_max_wait() is False


def test_reached_max_wait_positive():
    passenger = deepcopy(PASSENGER_0)

    in_elevator = False

    num_steps = 51

    for _ in range(num_steps):
        passenger.increment_step(in_elevator)

    assert passenger.reached_max_wait() is True


def test_moved_correct_direction_no_move():
    assert PASSENGER_0.moved_correct_direction(1, 1) is False


def test_moved_correct_direction_negative():
    assert PASSENGER_0.moved_correct_direction(2, 1) is False


def test_moved_correct_direction_positive():
    assert PASSENGER_0.moved_correct_direction(1, 2) is True


def test_moved_correct_direction_above_negative():
    assert PASSENGER_0.moved_correct_direction(6, 7) is False


def test_moved_correct_direction_above_positive():
    assert PASSENGER_0.moved_correct_direction(7, 6) is True
