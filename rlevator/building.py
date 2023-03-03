from rlevator.elevator import Elevator
from rlevator.passenger import Building
from rlevator.action import Action


class Building(object):

    def __init__(self, num_floors, num_elevators, max_queue=20, elevator_capacities=10, elevator_start_floors=None, elevator_bounds=None):
        """
        The Building object's two main components are the elevators and queues that
        passengers wait in until they can arrive in an elevator. It contains the interface
        for the elevators to take actions, handle Passenger arrivals and return the
        building state to the Environment.

        Args:
            num_floors : int
                Number of floors in the building
            num_elevators : int
                Number of elevators in the building
            max_queue : int
                Total number of passengers that will join an up or down queue before the
                next potential Passenger
            elevator_capacities : Union[int, List[int]]
                Either an integer defining the capacity of all elevators in the building
                or a list of num_elevators integers defining each individual elevator's
                capacity
            elevator_start_floors : Union[int, List[int]]
                Either an integer defining the capacity of all elevators in the building
                or a list of num_elevators integers defining each individual elevator's
                capacity
                If None, all elevators start at floor zero
            elevator_bounds : List[List[int]]
                Either None or a list of lists of num_elevators integers defining each individual elevator's minimum and maximum floors
                If None, all elevators can reach all floors
        """
        self.num_floors = num_floors
        self.num_elevators = num_elevators
        self.max_queue = max_queue

        # Initialize empty queues at each floor
        self._initialize_queues()
        # Initialize elevators with appropriate parameters
        self._initialize_elevators(elevator_capacities, elevator_start_floors, elevator_bounds)

    def _initialize_queues(self):
        """
        Create two lists for each floor to contain Passengers with destinations
        above and below them. Passengers will be loaded onto an elevator only from
        one queue at a time, with FIFO logic.
        """
        self.up_queues = [list() for _ in range(self.num_floors)]
        self.down_queues = [list() for _ in range(self.num_floors)]

    def _initialize_elevators(self, elevator_capacities, elevator_start_floors, elevator_bounds):
        """
        Based on the capacities, start floors and bounds, create the elevators that will
        be in use by the building.

        Args:
             elevator_capacities : Union[int, List[int]]
                Either an integer defining the capacity of all elevators in the building
                or a list of num_elevators integers defining each individual elevator's
                capacity
            elevator_start_floors : Union[int, List[int]]
                Either an integer defining the capacity of all elevators in the building
                or a list of num_elevators integers defining each individual elevator's
                capacity
                If None, all elevators start at floor zero
            elevator_bounds : List[List[int]]
                Either None or a list of lists of num_elevators integers defining each individual elevator's minimum and maximum floors
        """
        # Input error checking
        if elevator_capacities is None:
            raise Exception("Elevator capacities cannot be None")
        elif len(elevator_capacities) > 1 & len(elevator_capacities) < self.num_elevators:
            raise Exception("Elevator capacities should either be an integer or a list of integers equal to the number of elevators.")

        if elevator_start_floors is not None:
            if len(elevator_capacities) > 1 & len(elevator_capacities) < self.num_elevators:
                raise Exception("Elevator start floor should either be None or a list of integers equal to the number of elevators.")

        if elevator_bounds is not None:
            elif len(elevator_bounds) > 1 & len(elevator_bounds) < self.num_elevators:
                raise Exception("Elevator bounds should either be None or a list of list  integers equal to the number of elevators.")

        elevators = []

        for i in range(self.num_elevators):
            start_floor = 0 if elevator_start_floors is None else elevator_start_floors[i]
            capacity = elevator_capacities if len(elevator_capacities) == 1 else elevator_capacities[i]
            if elevator_bounds is not None:
                min_floor = 0
                max_floor = self.num_floors - 1
            else:
                min_floor = elevator_bounds[i][0]
                max_floor = elevator_bounds[i][1]

            elevators.append(Elevator(start_floor, capacity, min_floor, max_floor))

        self.elevators = elevators

    def execute_step(self, action_list):
        """
        Process a full step in the building, including pre-processing, actions,
        and post-processing.

        For the list of actions, execute them one by one for each elevator.

        After completing actions, increment the time step for all passengers.

        TODO: figure out what logging needs to happen here or if that's somewhere else

        Args:
             action_list : List[Action]
                List of Actions to be taken, one for each elevator in the building
        """
        if len(action_list) != self.num_elevators:
            raise Exception("The number of actions provided must match the number of elevators")

        # Preprocessing
        self.deboarding_passengers = []

        for elevator_num, action in enumerate(action_list):
            self.execute_action(elevator_num, action)

        # Post processing
        self.increment_step()

        # TODO: Logging/reporting

    def execute_action(self, elevator_num, action):
        """
        Execute the designed action on the elevator.

        Args:
            elevator_num : int
                Index of the elevator to take the action
            action : Action
                Action ENUM specifying which action to perform
        """
        # NOTE: Choosing to not use match capability in python 3.10 for compatibility
        if action == Action.DOWN:
            self.move_down(elevator_num)
        elif action == Action.UP:
            self.move_up(elevator_num)
        elif action == Action.WAIT:
            self.wait(elevator_num)
        elif action == Action.LOAD_UP:
            self.load_up(elevator_num)
        elif action == Action.LOAD_DOWN:
            self.load_down(elevator_num)
        elif action == Action.UNLOAD:
            self.unload(elevator_num)

    def move_down(self, elevator_num):
        self.elevators[elevator_num].move(-1)

    def move_up(self, elevator_num):
        self.elevators[elevator_num].move(1)

    def wait(self, elevator_num):
        """
        Do nothing. This avoids incorrect movement penalties.
        Ideally, this shouldn't be done if passengers are onboard.

        TODO: decide if this is correct behavior or if we move zero
        """
        pass

    def load_up(self, elevator_num):
        elevator = self.elevators[elevator_num]
        queue = self.up_queues[elevator.get_current_floor()]

        self.load(elevator, queue)

    def load_down(self, elevator_num):
        elevator = self.elevators[elevator_num]
        queue = self.down_queues[elevator.get_current_floor()]

        self.load(elevator, queue)

    def unload(self, elevator_num):
        elevator = self.elevators[elevator_num]
        self.deboarding_passengers += elevator.unload_passengers()

    def load(self, elevator, queue):
        """
        For a given elevator and queue on the same floor, attempt to fill the
        available spaces on the elevator from the queue as long as there are
        passengers left in the queue. We take passengers from the first in the
        list.

        Args:
            elevator_num : int
                Index of the elevator to take the action

        """
        boarding_passengers = []
        available_capacity = elevator.available_capacity()

        for _ in range(available_capacity):
            if len(queue) > 0:
                boarding_passengers.append(queue.pop(0))

        elevator.load_passengers(boarding_passengers)

    def _increment_step(self):
        """
        Increment a time step forwards for all passengers both in and out of elevators.
        """
        for queue in self.up_queues:
            for passenger in queue:
                passenger.increment_step(in_elevator=False)

        for queue in self.down_queues:
            for passenger in queue:
                passenger.increment_step(in_elevator=False)

        for elevator in self.elevators:
            for passenger in elevator.passengers:
                passenger.increment_step(in_elevator=True)

    def elevator_request_button_status(self):
        """
        Get the status of up/down elevator request buttons based on the queues.
        This will be used in the standard observation space.

        Returns: List[List[bool]]
            List of two lists, each of length num_floors that contains a boolean
            representing whether or not the up/down buttons are pressed by a
            nonzero number of passengers in the queue, respectively.
        """
        up_buttons = []
        down_buttons = []

        for i in range(self.num_floors):
            up_buttons.append(len(self.up_queues[i]) > 0)
            down_buttons.append(len(self.down_queues[i]) > 0)

        return [up_buttons, down_buttons]

