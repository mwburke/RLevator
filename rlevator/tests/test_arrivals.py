from rlevator.arrivals import PassengerArrivals

from numpy import average, array

NUM_FLOORS = 5
NUM_ELEVATORS = 1
DEFAULT_PARAMS = PassengerArrivals.generate_default_params(NUM_ELEVATORS,
                                                           NUM_FLOORS)

PA_0 = PassengerArrivals(**DEFAULT_PARAMS)


def test_generate_default_params_arrival_rates():
    actual_arrival_rates = [
        0.1,
        0.04,
        0.04,
        0.04,
        0.04
    ]

    tol = 1e-3

    arrival_rates_match = True
    for actual, generated in zip(actual_arrival_rates,
                                 DEFAULT_PARAMS['floor_arrival_rates']):
        arrival_rates_match &= abs(actual - generated) <= tol

    assert arrival_rates_match is True


def test_generate_default_params_destination_rates():

    actual_destination_rates = [
        [0, 0.25, 0.25, 0.25, 0.25],
        [0.9, 0, 0.0333, 0.0333, 0.0333],
        [0.9, 0.0333, 0, 0.0333, 0.0333],
        [0.9, 0.0333, 0.0333, 0, 0.0333],
        [0.9, 0.0333, 0.0333, 0.0333, 0],
    ]

    tol = 1e-3

    gen_rates = DEFAULT_PARAMS['floor_destination_rates']

    destination_rates_match = True
    for actual_arr, generated_arr in zip(actual_destination_rates, gen_rates):
        for actual, generated in zip(actual_arr, generated_arr):
            destination_rates_match &= abs(actual - generated) <= tol

    assert destination_rates_match is True


def test_arrivals_sampling():
    # Repeated runs, looking for correct averages?
    num_samples = 100000
    arrivals = []
    for _ in range(num_samples):
        arrivals.append(PA_0.generate_arrivals())

    avg_arrivals = average(array(arrivals), axis=0)

    # What is a good threshold here?
    tol = 0.3

    actual_arrival_rates = [
        0.1,
        0.04,
        0.04,
        0.04,
        0.04
    ]

    arrivals_match = True

    for actual, generated in zip(actual_arrival_rates, avg_arrivals):
        arrivals_match &= abs(actual - generated) <= tol

    assert bool(arrivals_match) is True


def test_destination_sampling():
    # Repeated runs, looking for correct averages?
    num_samples = 10000

    arrivals = [1, 1, 1, 1, 1]

    destinations = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]

    for _ in range(num_samples):
        destination_dicts = PA_0.assign_destinations(arrivals)
        for destination in destination_dicts:
            start_floor = destination['start_floor']
            destinations[start_floor][destination['destination_floor']] += 1

    destinations_arr = array(destinations).astype(float)
    destinations_arr /= num_samples

    tol = 0.3

    destinations_match = True

    actual_destination_rates = [
        [0, 0.25, 0.25, 0.25, 0.25],
        [0.9, 0, 0.0333, 0.0333, 0.0333],
        [0.9, 0.0333, 0, 0.0333, 0.0333],
        [0.9, 0.0333, 0.0333, 0, 0.0333],
        [0.9, 0.0333, 0.0333, 0.0333, 0],
    ]

    tol = 1e-3

    destination_rates_match = True
    for actual_arr, generated_arr in zip(actual_destination_rates,
                                         destinations_arr.tolist()):
        for actual, generated in zip(actual_arr, generated_arr):
            destination_rates_match &= abs(actual - generated) <= tol

    assert bool(destinations_match) is True
