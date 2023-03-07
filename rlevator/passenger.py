class Passenger(object):
    def __init__(self, start_step, start_floor, destination_floor,
                 max_wait_steps=50):
        """
        Passenger representation.

        Args:
            start_step : int
                Step number in the environment in which the passenger was
                created
            start_floor : int
                Initial floor number for which they arrived at the elevator
            destination_floor : int
                Floor number they are trying to reach through the elevator
            max_wait_steps : int
                Maximum number of steps they are willing to wait before they
                use the stairs
        """
        if start_floor == destination_floor:
            raise Exception("Start floor should not be equal to destination"
                            " floor")

        self.start_step = start_step
        self.start_floor = start_floor
        self.destination_floor = destination_floor
        self.max_wait_steps = max_wait_steps

        # Internal representation of how many steps have elapsed since they
        # first arrived at the elevator
        self.steps_age = 0
        # How long they have waited in line before entering the elevator
        self.steps_wait = 0

    def increment_step(self, in_elevator=False):
        """
        Increases the passenger step tracking upon environment step completion.
        Age increases every step, but wait only increases if they aren't on an
        elevator.

        Args:
            in_elevator : bool
                Flag as to whether or not the passenger is currently inside an
                elevator or waiting on a floor queue.
        """
        if not in_elevator:
            self.steps_wait += 1

        self.steps_age += 1

    def get_start_floor(self):
        return self.start_floro

    def get_destination_floor(self):
        return self.destination_floor

    def get_age(self):
        return self.steps_age

    def get_wait(self):
        return self.steps_wait

    def reached_max_wait(self):
        """
        Determines if the passenger has reached their max number of wait steps.
        TODO: determine if the passenger leaves or increases reward penalty
        when this condition is met. Could be an environment configuration
        """
        return self.steps_age > self.max_wait_steps

    def reached_destination(self, elevator_floor):
        return elevator_floor == self.destination_floor

    def moved_correct_direction(self, elevator_start_floor,
                                elevator_end_floor):
        """
        Determines if the elevator moved in direction of the passenger's
        destination floor or at least remained on the same floor. Main use is
        in the reward function to penalize elevators that move in the opposite
        direction of any passenger's destinations.

        Ideally, it should not be called is the start and end floors are
        equal, and the elevator did not move. However, in the case it does,
        not moving is counted as an incorrect direction since it made no
        progress.

        Args:
            elevator_start_floor : int
                Original floor that the elevator was located on before the step
            elevator_end_floor : int
                Original floor that the elevator was located on before the step

        Returns:
            bool
                Returns true if the end floor is closer to the destination
                floor than the original start floor of the elevator

        """
        orig_diff = abs(elevator_start_floor - self.destination_floor)
        move_diff = abs(elevator_end_floor - self.destination_floor)

        return move_diff < orig_diff
