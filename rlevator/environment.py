from collections import deque
from datetime import datetime
from copy import copy
import random

import numpy as np


class Passenger(object):
    def __init__(self, destination, start_time):
        """
        Args:
            destination : int, floor the user wants to go to
            start_time : datetime, time arrived in the elevator queue
                used for tracking metrics
        """
        self.start_time = start_time
        self.destination = destination


class Environment(object):

    def __init__(self, num_floors, num_elevators, capacity, arrival_rate, reward_function, max_queue=50, timestep=5, day_modifier=None, floor_hour_modifier=None, return_lobby_probs=None, start_time=datetime.now()):
        """
        TODO: document all these
        """
        self.num_floors = num_floors
        self.num_elevators = num_elevators
        self.capacity = capacity
        self.arrival_rate = arrival_rate
        self.reward_function = reward_function
        self.max_queue = 50
        self.timestep = timestep
        if day_modifier is None:
            day_modifier = np.ones((num_floors, 7))

        self.day_modifier = day_modifier
        if hour_modifier is None:
            hour_modifier = np.ones((num_floors, 24))
        self.hour_modifier = hour_modifier
        # Default 5% chance to go to random floor if not on bottom floor
        if return_lobby_probs is None:
            return_lobby_probs = np.array([0.05] * (num_floors - 1))
        self.return_lobby_probs = return_lobby_probs
        self.current_time = start_time
        self.reset()

    def reset(self):
        """
        Reset all of the elevators to the bottom floor and remove all passenger.
        Re-initialize the data structures to represent the base state.

        TODO: document data structures
        """
        self.done = False
        self.elevator_wait = [False] * self.num_elevators
        self.elevator_floors = np.zeros(self.num_elevators)
        self.floor_up_queues = [deque() for _ in range(self.num_floors)]
        self.floor_down_queues = [deque() for _ in range(self.num_floors)]
        self.elevator_passengers = [list for _ in range(self.num_floors)]
        self.floor_destinations = np.zeros((self.num_floors, self.num_floors))
        self.elevator_destinations = np.zeros((self.num_elevators, self.num_floors))

    def step(self, actions):
        """
        Move environemnt forwards a single step:
        - Advance time clock
        - Implement actions
            - Move elevators (if applicable)
            - Load/unload passengers (if applicable)
        - Determine rewards from actions and state
        - Calculate new arrivals
        - Emit data for agent(s) to consume

        Args:
            actions : ndarray, num_elevators length array of what actions
                each elevator intend to take in order

        Returns: 
            curr_partial_states : ndarray, numpy array of 
            TODO: document rest
        """
        curr_partial_states = self.get_partial_states()
        curr_state = self.get_state()

        real_actions = self.take_actions(actions)  # could modify illegal moves

        rewards = self.get_rewards()

        self.current_time += datetime.timedelta(0, self.timestep)

        self.passenger_arrivals()

        new_partial_states = self.get_partial_states()
        new_state = self.get_state()

        return curr_partial_states, curr_state, real_actions, rewards, new_partial_states, new_state, self.done

    def get_state(self):
        """
        Get the current detailed state in a numpy array including the
        floor locations of all elevators, destinations of passengers waiting
        in queues on each floor, and destinations of passengers currently
        inside elevators.

        TODO: do we consider time (hour/day) as part of the state?

        Returns:
            state : ndarray, 1D numpy array containing above information
        """
        state = np.concatenate(
            (
                self.elevator_floors, 
                self.floor_destinations.flatten(),
                self.elevator_destinations.flatten()
            )
        )

        return state

    def get_partial_states(self):
        """
        Get an incomplete representation of the state in a numpy array.
        Only information that elevators would have in a real scenario:
        - Up/down requests for each floor
        - Floor requests in each elevator
    
        TODO: do we consider time (hour/day) as part of the state?

        Returns: 
            partial_state : list of ndarrays, list of numpy arrays, one
                for each elevator containing the floor locations of all
                elevators, current buttons pressed in the elevator, and
                the up/down buttons pressed on all floors
        """
        floor_buttons = self.floor_buttons()

        partial_state = [
            np.concatenate(
                self.elevator_floors,
                self.elevator_buttons(elevator),
                floor_buttons
            )
            for elevator in range(self.num_elevators)
        ]

        return partial_state

    def elevator_buttons(self, elevator):
        """
        Convert the destinations for this elevator into a numpy array of
        ones and zeros representing at least one passenger with a destination
        on each floor.
        """
        presses = [
            int(sum(self.floor_destinations[elevator] == floor) > 0)
            for floor in range(self.num_floors)
        ]

        return np.array(presses)

    def floor_buttons(self):
        """
        For each floor, check if any destinations below and above the floor
        to see if the up/down buttons were pressed. Aggregate these into a
        numpy array 2x the number of floors for user in the partial state observations.
        """
        presses = []
        for floor in range(self.num_floors):
            presses.append(int(sum(self.elevator_destinations[floor] < floor) > 0))
            presses.append(int(sum(self.elevator_destinations[floor] > floor) > 0))
        
        return np.array(presses)

    def take_actions(self, actions):
        """
        Take in intended actions for each elevator and process them in order of 
        elevator number. 

        TODO: decide in what order to take actions
              only really has effects when elevators picking up on same floor
              at the same time with nonzero passenger queue

        If action is legal, then allow it. Otherwise, override with "wait" action.

        Actions:
            0: Move up one floor
               Illegal when on top floor
            1: Move down one floor
               Illegal when on bottom floor
            2: Load passengers from up queue on current elevator floor
               Must be followed by wait action because it is a two-timestep action
               Only loads passengers if any in up queue, otherwise no effect
            3: Load passengers from down queue on current elevator floor
               Must be followed by wait action because it is a two-timestep action
               Only loads passengers if any in down queue
            4: Unload passengers on the current floor
               Must be followed by wait action because it is a two-timestep action
               Only unloads passengers if any have current floor as destination
            5: Wait
               Has no effect on the current state
        """
        final_actions = copy(actions)

        for elevator, action in enumerate(actions):
            action = int(action)
            # Enforce waiting step after load or unload
            if self.elevator_wait[elevator]:
                final_actions[elevator] = 5
                self.elevator_wait[elevator] = False
            else:
                # Move up
                if action == 0:
                    if self.elevator_floors[elevator] != (self.num_floors - 1):
                        self.elevator_floors[elevator] += 1
                    else:
                        final_actions[elevator] = 5
                # Move down
                elif action == 1:
                    if self.elevator_floors[elevator] != 0:
                        self.elevator_floors[elevator] -= 1
                    else:
                        final_actions[elevator] = 5
                # Load up queue
                elif action == 2:
                    floor = self.elevator_floors[elevator]
                    while len(self.floor_up_queues[floor]) > 0:
                        if len(self.elevator_passengers[elevator]) < self.capacity:
                            passenger_dest = self.floor_up_queues[floor][0].destination
                            self.floor_destinations[floor][passenger_dest] -= 1
                            self.elevator_destinations[elevator][passenger_dest] += 1
                            self.elevator_passengers[elevator].append(self.floor_up_queues[floor].popleft())
                        else:
                            break
                # Load down queue
                elif action == 3:
                    floor = self.elevator_floors[elevator]
                    while len(self.floor_down_queues[floor]) > 0:
                        if len(self.elevator_passengers[elevator]) < self.capacity:
                            passenger_dest = self.floor_down_queues[floor][0].destination
                            self.floor_destinations[floor][passenger_dest] -= 1
                            self.elevator_destinations[elevator][passenger_dest] += 1
                            self.elevator_passengers[elevator].append(self.floor_down_queues[floor].popleft())
                        else:
                            break
                # Unload passengers
                elif action == 4:
                    floor = self.elevator_floors[elevator]
                    passengers_copy = copy(passenger in self.elevator_passengers[elevator])
                    for passenger in passengers_copy:
                        if passenger.destination == floor:
                            self.elevator_passengers[elevator].remove(passenger)
                            self.elevator_destinations[elevator][passenger_dest] -= 1
                # Do nothing
                elif action == 5:
                    pass

        return final_actions                                                        

    def passenger_arrivals(self):
        """
        For each floor:
        - take into account its arrival rate, and the
           modifiers for the current hour and day to determine how many
           individuals arrived during a single timestep
        - note their arrival times
          TODO: going with middle of time step, if multiple, split into equal times?
        - assign a destination floor for each of them
        - add them to the appropriate up/down queu based on destination
        """
        # Monday is 0
        weekday = self.current_time.weekday()
        hour = self.current_time.hour

        for floor in range(self.num_floors):
            arrival_rate = self.arrival_rate[floor]
            arrival_rate *= self.day_modifier[floor][weekday]
            arrival_rate *= self.hour_modifier[floor][hour]

            num_passengers = np.random.poisson(arrival_rate)
            
            for _ in range(num_passengers):
                destination = self.assign_destination(floor)
                passenger = Passenger(destination, self.current_time + datetime.timedelta(0, self.timestep / 2))
                if destination > floor:
                    self.floor_up_queues[floor].append(passenger)
                else:
                    self.floor_down_queues[floor].append(passenger)

    def assign_destination(self, floor):
        """
        If on bottom floor, go to random floor.
        If not on bottom floor, predefined chance to go to a random floor
            other than the one they're on including the bottom floor.
            Otherwise they go back to the bottom floor.

        Returns:
            destination : int, floor number the passenger wants to go to
        """
        if floor == 0:
            destination = random.randint(0, self.num_floors)
        else:
            if random.random() < self.return_lobby_probs[floor - 1]:
                options = [i for i in range(self.num_floors) if i != floor]
                destination = random.choice(options)
            else:
                destination = 0
        
        return destination

    def get_rewards(self):
        """
        Use the stored reward function to return rewards for each
        agent (could be a single agent) based on the state.

        TODO: figure out if this is the right way to do this
              can we assign overall pasenger waiting negative rewards to specific elevators?
              how about passing in an array of weights to known situations rather than a function?
              do we need the flexibility to have a custom function or does that make it more error prone?
        """
        state = self.get_state()
        rewards = self.reward_function(state)

        return rewards
