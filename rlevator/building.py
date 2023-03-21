from rlevator.elevator import Elevator
from rlevator.actions import Action

from numpy import array, int8


class Building(object):

    def __init__(self, num_floors, num_elevators, max_queue=20,
                 elevator_capacities=10, elevator_start_floors=None,
                 elevator_bounds=None):
        """
        The Building object's two main components are the elevators and queues
        that passengers wait in until they can arrive in an elevator. It
        contains the interface for the elevators to take actions, handle
        Passenger arrivals and return the building state to the Environment.

        Args:
            num_floors : int
                Number of floors in the building
            num_elevators : int
                Number of elevators in the building
            max_queue : int
                Total number of passengers that will join an up or down queue
                before the next potential Passenger
            elevator_capacities : Union[int, List[int]]
                Either an integer defining the capacity of all elevators in
                the building or a list of num_elevators integers defining each
                individual elevator's capacity
            elevator_start_floors : Union[int, List[int]]
                Either an integer defining the capacity of all elevators in
                the building or a list of num_elevators integers defining each
                individual elevator's capacity

                If None, all elevators start at floor zero
            elevator_bounds : List[List[int]]
                Either None or a list of lists of num_elevators integers
                defining each individual elevator's minimum and maximum floors

                If None, all elevators can reach all floors
        """
        self.num_floors = num_floors
        self.num_elevators = num_elevators
        self.max_queue = max_queue

        self.elevator_capacities = elevator_capacities
        self.elevator_start_floors = elevator_start_floors
        self.elevator_bounds = elevator_bounds

        self.reset()

    def reset(self):
        """
        Re-initializes all queues and elevators to start the building as a
        blank slate.
        """
        # Initialize empty queues at each floor
        self._initialize_queues()
        # Initialize elevators with appropriate parameters
        self._initialize_elevators()

    def _initialize_queues(self):
        """
        Create two lists for each floor to contain Passengers with destinations
        above and below them. Passengers will be loaded onto an elevator only
        from one queue at a time, with FIFO logic.
        """
        self.up_queues = [list() for _ in range(self.num_floors)]
        self.down_queues = [list() for _ in range(self.num_floors)]
        self.rejected_queue_passengers = []
        self.deboarding_passengers = []
        self.reached_max_wait_passengers = []
        self.count_correct_direction_passengers = 0
        self.count_incorrect_direction_passengers = 0

    def _initialize_elevators(self):
        """
        Based on the capacities, start floors and bounds, create the elevators
        that will be in use by the building.

        Args:
             elevator_capacities : Union[int, List[int]]
                Either an integer defining the capacity of all elevators in
                the building or a list of num_elevators integers defining each
                individual elevator's
                capacity
            elevator_start_floors : Union[int, List[int]]
                Either an integer defining the capacity of all elevators in the
                building or a list of num_elevators integers defining each
                individual elevator's capacity

                If None, all elevators start at floor zero
            elevator_bounds : List[List[int]]
                Either None or a list of lists of num_elevators integers
                defining each individual elevator's minimum and maximum floors
        """
        # Input error checking
        if self.elevator_capacities is None:
            raise Exception("Elevator capacities cannot be None")
        elif type(self.elevator_capacities) is not int:
            if len(self.elevator_capacities) < self.num_elevators:
                raise Exception("Elevator capacities should either be an "
                                "integer or a list of integers equal to the "
                                "number of elevators.")

        if self.elevator_start_floors is not None:
            if len(self.elevator_start_floors) != self.num_elevators:
                raise Exception("Elevator start floor should either be None "
                                "or a list of integers equal to the number of "
                                "elevators.")

        if self.elevator_bounds is not None:
            if len(self.elevator_bounds) != self.num_elevators:
                raise Exception("Elevator bounds should either be None or a "
                                "list of list  integers equal to the number "
                                "of elevators.")

        elevators = []

        for i in range(self.num_elevators):
            if self.elevator_start_floors is None:
                start_floor = 0
            else:
                start_floor = self.elevator_start_floors[i]

            if type(self.elevator_capacities) is int:
                capacity = self.elevator_capacities
            else:
                capacity = self.elevator_capacities[i]

            if self.elevator_bounds is None:
                min_floor = 0
                max_floor = self.num_floors - 1
            else:
                min_floor = self.elevator_bounds[i][0]
                max_floor = self.elevator_bounds[i][1]

            elevators.append(
                Elevator(start_floor, capacity, min_floor, max_floor)
            )

        self.elevators = elevators

    def get_queue(self, floor, up=False):
        """
        Get a queue of passengers on a given floor.

        Args:
            floor : int
                Floor number to get the queue from
            up : bool
                Boolean denoting whether to get the up floor if True
                or the down floor is False

        Returns: List[Passenger]
        """
        if up:
            return self.up_queues[floor]
        return self.down_queues[floor]

    def execute_step(self, arrived_passengers, action_list):
        """
        Process a full step in the building, including pre-processing,
        passenger arrivals, actions, and post-processing.

        For the list of actions, execute them one by one for each elevator.

        After completing actions, increment the time step for all passengers.

        Args:
            arrived_passengers : List[Passenger]
                List of passengers that arrived at queues
            action_list : List[Action]
                List of Actions to be taken, one for each elevator in the
                building
        """
        if len(action_list) != self.num_elevators:
            raise Exception("The number of actions provided must match the "
                            "number of elevators")

        # Preprocessing, reset step tracking values
        self.deboarding_passengers = []
        self.rejected_queue_passengers = []
        self.reached_max_wait_passengers = []
        self.count_correct_direction_passengers = 0
        self.count_incorrect_direction_passengers = 0

        # Handle passengers that have now exceeded max wait time
        self.remove_max_wait_passengers()

        # Add new passengers to queues
        self.add_arrivals_to_queues(arrived_passengers)

        # Execute actions
        for elevator_num, action in enumerate(action_list):
            self.execute_action(elevator_num, action)

        # Post processing
        self._increment_step()

        # TODO: Logging/reporting

    def remove_max_wait_passengers(self):
        """
        Go through all queues and remove passengers that have reached their
        max wait time.
        """
        for i, queue in enumerate(self.up_queues):
            new_queue = self.remove_max_wait_from_queue(queue)
            self.up_queues[i] = new_queue

        for i, queue in enumerate(self.down_queues):
            new_queue = self.remove_max_wait_from_queue(queue)
            self.down_queues[i] = new_queue

    def remove_max_wait_from_queue(self, queue):
        """
        Go through each passenger in the queue, and if they have reached their
        maximum wait time, remove them from the queue and add them to the list
        that tracks passengers who have voluntarily left the queue.

        Returns the updated queue with passengers who have not reached their
        max wait time.

        Args:
            queue : List[Passenger]
                Elevator queue of passengers to be checked for max wait times

        Returns: List[Passenger]
        """
        new_queue = []
        for passenger in queue:
            if passenger.reached_max_wait():
                self.reached_max_wait_passengers.append(passenger)
            else:
                new_queue.append(passenger)

        return new_queue

    def add_arrivals_to_queues(self, passengers):
        """
        Process all new passenger arrivals by adding them to the appropriate
        floor queues.

        Args:
            passengers : List[Passenger]
        """
        for passenger in passengers:
            self.add_passenger_to_queue(passenger)

    def add_passenger_to_queue(self, passenger):
        """
        For a passenger, determine their starting floor and whether they would
        enter the up or down queue depending on their destination floor.

        If the queue is not at max length, then add them to that queue.
        Otherwise, add them to a list of passengers that rejected joining the
        queue because it was too long, to be included in the reward function
        penalty.

        Args:
            passenger : Passenger
                Passenger arrival to be processed
        """
        start_floor = passenger.get_start_floor()

        if passenger.get_destination_floor() > start_floor:
            try_queue = self.up_queues[start_floor]
        elif passenger.get_destination_floor() < start_floor:
            try_queue = self.down_queues[start_floor]
        else:
            raise Exception("Passenger's destination floor cannot be the same "
                            "as start floor")

        if len(try_queue) < self.max_queue:
            try_queue.append(passenger)
        else:
            self.rejected_queue_passengers.append(passenger)

    def get_rejected_queue_passengers(self):
        """
        Get the passengers that tried to enter a queue on this turn while the
        queue already was at max capacity.

        Return: List[Passenger]
        """
        return self.rejected_queue_passengers

    def get_deboarding_passengers(self):
        """
        Get the passengers that have deboarded the elevators due to an UNLOAD
        action.

        Return: List[Passenger]
        """
        return self.deboarding_passengers

    def execute_action(self, elevator_num, action):
        """
        Execute the designed action on the elevator.

        Args:
            elevator_num : int
                Index of the elevator to take the action
            action : Action
                Action ENUM specifying which action to perform
        """
        # NOTE: Choosing to not use match capability in python 3.10
        # for compatibility
        if action == Action.MOVE_DOWN:
            self.move_down(elevator_num)
        elif action == Action.MOVE_UP:
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
        start_floor = self.elevators[elevator_num].get_current_floor()
        self.elevators[elevator_num].move(-1)
        self.update_move_direction_counts(elevator_num, start_floor)

    def move_up(self, elevator_num):
        start_floor = self.elevators[elevator_num].get_current_floor()
        self.elevators[elevator_num].move(1)
        self.update_move_direction_counts(elevator_num, start_floor)

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
            queue : List[Passenger]
                Elevator queue of Passengers waiting to board in the specified
                direction.
        """
        boarding_passengers = []
        available_capacity = elevator.available_capacity()

        for _ in range(available_capacity):
            if len(queue) > 0:
                boarding_passengers.append(queue.pop(0))

        elevator.load_passengers(boarding_passengers)

    def update_move_direction_counts(self, elevator_num, start_floor):
        elevator = self.elevators[elevator_num]
        self.count_correct_direction_passengers += \
            elevator.count_correct_move_passengers(start_floor)
        self.count_incorrect_direction_passengers += \
            elevator.count_incorrect_move_passengers(start_floor)

    def _increment_step(self):
        """
        Increment a time step forwards for all passengers both in and out
        of elevators.
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

    def elevator_destination_bool_list(self):
        """
        Return a list of lists of booleans representing whether or not there is
        at least one passenger on each elevator wanting to go to each floor or
        not.

        Returns: List[List[bool]]
            Lists for each elevator containing a list of booleans, one for each
            floor where true means at least one passenger has that floor as
            theri destination.
        """
        destinations = []
        for i in range(self.num_elevators):
            destinations.append(self.elevator[i].get_destination_bool_list())

        return destinations

    def elevator_destinations(self):
        """
        Return a list of lists of ints representing that there is at least one
        passenger on each elevator wanting to go to that floor.

        Returns: List[List[int]]
            Lists for each elevator containing a list of ints denoting the
            floors that its passengers have as their destinations.
        """
        destinations = []
        for i in range(self.num_elevators):
            destinations.append(self.elevator[i].get_destinations())

        return destinations

    def queue_request_button_statuses(self):
        """
        Get the status of up/down elevator request buttons based on the queues.
        This will be used in the standard observation space.

        Returns: List[List[bool]]
            List of two lists, each of length num_floors that contains a bool
            representing whether or not the up/down buttons are pressed by a
            nonzero number of passengers in the queue, respectively.
        """
        up_buttons = []
        down_buttons = []

        for i in range(self.num_floors):
            up_buttons.append(len(self.up_queues[i]) > 0)
            down_buttons.append(len(self.down_queues[i]) > 0)

        return [up_buttons, down_buttons]

    def get_reward_components(self):
        """
        Collect all of the different components that are used in calculating
        the environment reward given the current state. Here is a list of the
        components and a brief description of what they are and whether the
        reward is positive or negative.

        deboarding_passengers: positive reward for passengers successfully
            dropped off at their destinations
        rejected_queue_passengers: negative reward for passengers that tried
            to join a full queue and could not
        reached_max_wait_passengers: negative reward for passengers that
            reached their maximum wait time and were
        passengers_elevator: negative reward for the total number
            of passengers currently still in elevators
        passengers_queues: negative reward for the total number
            of passengers currently still in queues
        passengers_move_correct_direction: positive reward for the number of
            passengers that were moved in the correct direction of their
            destination in the elevator
        passengers_move_incorrect_direction: megatove reward for the number of
            passengers that were moved in the incorrect direction of their
            destination in the elevator

        Returns: dict
        """
        components = dict()

        components['deboarding_passengers'] = self.deboarding_passengers
        components['rejected_queue_passengers'] = \
            self.rejected_queue_passengers
        components['reached_max_wait_passengers'] = \
            self.reached_max_wait_passengers
        components['count_correct_direction_passengers'] = \
            self.count_correct_direction_passengers
        components['count_incorrect_direction_passengers'] = \
            self.count_incorrect_direction_passengers

        passengers_elevator = 0
        for elevator in self.elevators:
            passengers_elevator += elevator.get_count_passengers()
        components['passengers_elevator'] = passengers_elevator

        passengers_queue = 0
        for i in range(self.num_floors):
            passengers_queue += len(self.up_queues[i])
            passengers_queue += len(self.down_queues[i])
        components['passengers_queue'] = passengers_queue

        return components

    def get_observation_limited(self):
        """
        Collect data for a limited observation of the system. Specifically,
        the only normal available data to an elevator system are what buttons
        are pressed on each floor for the queues, as well as the destination
        floor buttons within the elevators. We don't know any of the
        passengers' true destinations in the queue or how many passengers
        pressed the destination buttons. Additionally, the elevators know what
        floors they are currently on.

        Returns: dict
            Returns a dictionary containing two numpy arrays of boolean

        """
        observation = dict()

        observation['elevator_buttons'] = array(
            self.elevator_destination_bool_list(), astype=int8
        )
        observation['queue_buttons'] = array(
            self.queue_request_button_statuses(), astype=int8
        )

        observation['elevator_floors'] = array([
            elevator.get_current_floor() for elevator in self.elevators
        ], astype=int8)

        return observation
