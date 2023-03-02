class Elevator(object):

    def __init__(self, start_floor, capacity, min_floor, max_floor):
        """
        Elevator representation. Holds passengers and is aware of its own capacity
        and general passenger destinations. The destinations are stored as a list of
        booleans, with true meaning that the button has been clicked and the corresponding
        passengers have not yet been unloaded onto that destination floor.

        Floor zero is the bottom floor and it goes up from there.

        Args:
            start_floor : int
                Floor number in the building that the elevator starts off at.
            min_floor : int
                Bottom floor that the elevator can access
            max_floor : int
                Top floor that the elevator can access
            capacity : int
                Total number of passengers that the elevator can hold at any one time.
        """

        self.floor = start_floor
        self.passengers = []
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.capacity = capacity

        self._update_destinations()

    def _update_destinations(self):
        """
        Reset the destinations to false, and then reinitialize based on current passengers.
        """
        destinations = set()

        for passenger in self.passengers:
            destinations.add(passenger.get_destination_floor())

        self.destinations = destinations

    def get_destination_bool_list(self):
        """
        Returns the boolean list of destination identifiers for each floor
        starting at the min_floor and working upwards
        """
        destinations = []

        for floor in range(self.min_floor, self.max_floor + 1):
            if floor in self.destinations:
                destinations.append(True)
            else:
                destinations.append(False)

        return destinations

    def get_current_floor(self):
        return self.floor

    def destination_floors(self):
        """
        Returns a list of the floors that are destinations for at least one passenger.
        """
        return self.destinations

    def get_capacity(self):
        return self.capacity

    def get_min_floor(self):
        return self.min_floor

    def get_max_floor(self):
        return self.max_floor

    def get_floor_bounds(self):
        return [self.min_floor, self.max_floor]

    def get_count_passengers(self):
        return len(self.passengers)

    def available_capacity(self):
        """
        Return the number of available spots for passengers on the elevator.
        """
        return self.capacity - len(self.passengers)

    def move(self, floor_diff):
        """
        Move the elevator based on the floor difference provided. Clamp the floor number
        to be between the minimum and maximum floors. This means that if the move function
        is called and it would be out of bounds, it only goes to the limit and will not
        exceed.

        TODO: decide if we want to raise and exception for out of bounds errors

        Args:
            floor_diff : int
                Integer number of floors to move based on floor number.
        """
        new_floor = max(min(self.floor + floor_diff, self.max_floor), self.min_floor)

        self.floor = new_floor

    def load_passengers(self, passengers):
        """
        Load new passengers onto the elevator and update destinations accordingly.

        Args:
            passengers : List[Passenger]
        """
        if len(passengers) > self.available_capacity():
            raise Exception("The elevator cannot handle this many passengers and will be over capacity")

        self.passengers += passengers

        self._update_destinations()

    def unload_passengers(self):
        """
        Identify all passengers with the current floor as the destination and return
        them in a list. Set the passengers list to be the remaining passengers that
        were not returned. There is no limit to the number of passengers that can
        be unloaded at one time.

        Returns:
            List[Passenger]
        """
        unload_passengers = []
        stay_passengers = []

        for passenger in self.passengers:
            if passenger.reached_destination(self.floor):
                unload_passengers.append(passenger)
            else:
                stay_passengers.append(passenger)

        self.passengers = stay_passengers

        self._update_destinations()

        return unload_passengers

    def count_correct_move_passengers(self, start_floor):
        """
        After an elevator has moved, count the number of passengers for which the
        move was in the correct direction for their destination.

        Args:
            start_floor : int
                The previous floor that the elevator was on before moving. The end
                floor is the current floor the elevator is on since it has already moved.

        Returns:
            int
                Number of passengers with the desired move direction.
        """
        move_count = 0

        for passenger in self.passengers:
            if passenger.moved_correct_direction(start_floor, self.floor):
                move_count += 1

        return move_count

    def count_incorrect_move_passengers(self, start_floor):
        """
        After an elevator has moved, count the number of passengers for which the
        move was in the incorrect direction for their destination.

        Args:
            start_floor : int
                The previous floor that the elevator was on before moving. The end
                floor is the current floor the elevator is on since it has already moved.

        Returns:
            int
                Number of passengers with the incorrect move direction.
        """
        move_count = 0

        for passenger in self.passengers:
            if not passenger.moved_correct_direction(start_floor, self.floor):
                move_count += 1

        return move_count

    def increment_passenger_steps(self):
        """
        Calls the step increment function for every passenger in the elevator with the
        argument that they are in the elevator so the wait age is not increased.
        """
        for passenger in self.passengers:
            passenger.increment_step(in_elevator=True)
