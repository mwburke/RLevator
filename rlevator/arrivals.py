from rlevator.passenger import Passenger

from numpy.random import poisson, choice


class PassengerArrivals(object):
    """
    This class stores the parameters used to define how often Passengers
    arrive on each floor, and what their destinations will be depending
    on their arrival floor.

    Arrivals are simulated from the Poisson distribution, and the
    destinations are chosen from an array of probabilities.
    """

    def __init__(self, num_floors, floor_arrival_rates,
                 floor_destination_rates):
        """
        This class stores the parameters used to define how often Passengers
        arrive on each floor and what their destinations will be.

        Args:
            num_floors : int
                Number of floors in the building
            floor_arrival_rates : List[float]
                List of lambda values to use for Poisson arrivals in a single
                timestep. This value is the average rate of arrivals within the
                time period.

                This list should be the same length as the number of floors in
                the Building.
            floor_destination_rates : List[List[float]]
                List of probabilities that define which destination floor a
                Passenger will have based on their arrival floor.
                The sum of all rates should sum to one, and the probability of
                having the same destination as start floor should be zero.

                This list should be the same length as the number of floors in
                the Building, and each list within that list should also equal
                the number of floors in the Building.
        """
        if len(floor_arrival_rates) != num_floors:
            raise Exception("The number of floor arrival rates should be "
                            "equal to the number of floors in the building")

        if len(floor_destination_rates) != num_floors:
            raise Exception("The number of floor destination rates should be "
                            "equal to the number of floors in the building")

        if len(floor_destination_rates[0]) != num_floors:
            raise Exception("The floor destination rates for each floor "
                            "should be equal to the number of floors")

        self.num_floors = num_floors
        self.floor_arrival_rates = floor_arrival_rates
        self.floor_destination_rates = floor_destination_rates

    @staticmethod
    def generate_default_params(num_elevators, num_floors):
        """
        TODO: once environment is ready, do testing to determine the actual
        arrival rates to use as a baseline.

        In the case where we don't want to provide custom rates, we want to
        provide a recommended set of the simplest possible case:

        Most arrivals will take place at the bottom floor with destinations
        split evenly among all nonzero floors.

        All arrivals not on the bottom floor will happen with even frequency
        across all floors. Their destinations will mostly be the bottom floor
        with all other destinations split evenly among other floors.

        Args:
            num_elevators : int
                Number of elevators in the building
            num_floors : int
                Number of floors in the buildilng

        Returns: Dict
            Dictionary containing floor_arrival_rates and
            floor_destination_rates with sizes num_floors and num_floors x
            num_floors, respectively.
        """
        GROUND_FLOOR_LAMBDA = 0.5 * num_elevators
        OTHER_FLOOR_LAMBDA = 0.5 * num_elevators / num_floors

        GROUND_FLOOR_DEST_PROB = 0.8
        OTHER_FLOOR_DEST_PROB = (1 - GROUND_FLOOR_DEST_PROB) / (num_floors - 2)

        floor_arrival_rates = [GROUND_FLOOR_LAMBDA]
        for _ in range(num_floors - 1):
            floor_arrival_rates.append(OTHER_FLOOR_LAMBDA)

        floor_destination_rates = [
            [0] + [1 / (num_floors - 1) for _ in range(num_floors - 1)]
        ]

        for i in range(1, num_floors):
            floor_probs = []
            for j in range(0, num_floors):
                if j == 0:
                    floor_probs.append(GROUND_FLOOR_DEST_PROB)
                elif i == j:
                    floor_probs.append(0)
                else:
                    floor_probs.append(OTHER_FLOOR_DEST_PROB)
            floor_destination_rates.append(floor_probs)
        return {
            'num_floors': num_floors,
            'floor_arrival_rates': floor_arrival_rates,
            'floor_destination_rates': floor_destination_rates
        }

    def generate_arrivals(self):
        """
        Use the Poisson distribution sampling to generate the numbe  r of
        Passenger arrivals on each floor in the time step.

        Returns: List[int]
            Returns a list of the number of Passenger arrivals on each floor.
            List length should equal the number of floors in the building.
        """
        return poisson(self.floor_arrival_rates).tolist()

    def assign_destinations(self, arrivals):
        """
        For each arrival on each floor, generate a generation using the
        pre-defined probabilities for each start floor.

        Args:
            arrivals : List[int]
                List of the number of Passenger arrivals on each floor

        Returns: List[Dict]
            Returns a flattened list of dictionaries with start_floor and
            destination_floor for each arrived passenger.
        """
        floor_options = [i for i in range(self.num_floors)]
        destinations = []

        for floor, arrival_num in enumerate(arrivals):
            for _ in range(arrival_num):
                destination_floor = choice(
                    floor_options,
                    p=self.floor_destination_rates[floor]
                )
                destinations.append({
                    'start_floor': floor,
                    'destination_floor': destination_floor
                })

        return destinations

    def generate_passengers(self, curr_time_step, max_wait_steps):
        """
        For the current time step, use the arrival and destination rates to
        generate new passengers for the building.

        Args:
            curr_time_step : int
                Current time step of the environment
            max_wait_steps : int
                Maximum number of steps the Passengers will wait in the queue
                before they leave it.

        Returns: List[Passenger]
            List of passengers to be added to the building's queues
        """
        arrivals = self.generate_arrivals()
        dest_info = self.assign_destinations(arrivals)

        new_passengers = []

        for passenger_params in dest_info:
            passenger_params.update({
                'start_step': curr_time_step,
                'max_wait_steps': max_wait_steps
            })
            new_passengers.append(Passenger(**passenger_params))

        return new_passengers
