from collections import deque
from datetime import datetime

import numpy as np


class Person(object):
    def __init__(self, destination, start_time):
        self.start_time = start_time
        self.destination = destination


class ElevatorEnv(object):

    def __init__(self, num_floors, num_elevators, capacity, arrival_rate, reward_function, max_queue=50, step_time=5, day_modifier=None, floor_hour_modifier=None, start_time=datetime.now()):
        """
        TODO: document all these
        """
        self.num_floors = num_floors
        self.num_elevators = num_elevators
        self.capacity = capacity
        self.arrival_rate = arrival_rate
        self.reward_function = reward_function
        self.max_queue = 50
        self.step_time = step_time
        if day_modifier is None:
            day_modifier = np.ones((num_floors, 7))

        self.day_modifier = day_modifier
        if hour_modifier is None:
            hour_modifier = np.ones((num_floors, 24))
        self.hour_modifier = hour_modifier
        self.current_time = start_time
        self.reset()

    def reset(self):
        """
        Reset all of the elevators to the bottom floor and remove all people.
        Re-initialize the data structures to represent the base state.

        TODO: document data structures
        """
        self.done = False
        self.elevator_wait = [False] * self.num_elevators
        self.elevator_floors = np.zeros(self.num_elevators)
        self.floor_up_queues = [deque() for _ in range(self.num_floors)]
        self.floor_down_queues = [deque() for _ in range(self.num_floors)]


    def step(self, actions):
        """
        Move environemnt forwards a single step:
        - Advance time clock
        - Move elevators (if applicable)
        - Load/unload passengers (if applicable)
        - Determine rewards from actions and state
        - Calculate new arrivals
        - Emit data for

        Args:
            actions : ndarray, num_elevators length array of what actions
                each elevator intend to take in order

        Returns
        """
        curr_partial_states = self.get_partial_states()
        curr_state = self.get_state()

        self.take_actions(actions)

        pass

    def get_state(self):
        """
        Get the current state in a numpy array
        """
        pass

    def get_partial_states(self):
        """
        Get an incomplete representation of the state in a numpy array.
        Only information that elevators would have in a real scenario:
        - Up/down requests for each floor
        - Floor requests in each elevator
        """
        pass

    def take_actions(self, actions):
        """
        Take in intended actions for each elevator.
        If action is legal, then allow it.
        Otherwise, override with "wait" action.

        TODO: define actions and which action number values correspond to them

        TODO: define illegal actions/situations, move out of bounds, two-step loading/unloading
        """
        pass


    def get_arrivals(self):
        """
        For each floor:
        - take into account its arrival rate, and the
           modifiers for the current hour and day to determine how many
           individuals arrived during a single timestep
        - note their arrival times  TODO: beginning of step? middle?
        - assign a destination floor for each of them
        """
        pass

    def get_reward(self):
        """
        Use the stored reward function to return rewards for each
        agent (could be a single agent) based on the state.

        TODO: figure out if this is the right way to do this, can we assign overall people waiting negative rewards to specific elevators?
        """
        state = self.get_state()
        rewards = self.reward_function(state)

        return rewards
