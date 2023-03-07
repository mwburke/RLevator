from rlevator.building import Building
# from rlevator.elevator import Elevator
# from rlevator.passenger import Passenger

# from copy import deepcopy


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
    elevator_bounds=[[0, 10], [0, 10]]
)


"""
BUILDING TESTS

"""
