from rlevator.arrivals import PassengerArrivals
from rlevator.building import Building
from rlevator.actions import Action

import gymnasium as gym
from gymnasium import spaces


# TODO: these need testing to determine decent defaults
DEFAULT_REWARD_WEIGHTS = dict(
    deboarding_passengers=10,
    rejected_queue_passengers=-10,
    reached_max_wait_passengers=-10,
    passengers_elevator=-1,
    passengers_queues=-2,
    passengers_move_correct_direction=2,
    passengers_move_incorrect_direction=-5
)


class RLevatorEnv(gym.Env):
    def __init__(self, render_mode=None, num_floors=10, max_queue=20,
                 num_elevators=1, passenger_generator=None,
                 elevator_params={'elevator_capacities': 10},
                 observation_type='limited', reward_weights=None,
                 termination_steps=200):
        """
        Create gymnasium environment containing a building with elevators,
        floors and passengers.

        Args:
            render_mode : str
                Render mode
            num_floors : int
                Number of floors in the building
            num_elevators : int
                Number of elevators in the building
            max_queue : int
                Total number of passengers that will join an up or down queue
                before the next potential Passenger
            passenger_generator : PassengerArrival
                Passenger arrival generator or None. If None, it will use a
                default generator based on the number of floors and elevators.
            elevator_params : dict
                Dictionary with the elevator_capacities, elevator_start_floors,
                and elevator_bounds from the Building constructor. Please see
                constructor definition for additional details on definition.
            observation_type : str
                Type of observation to use for learning. Currently, only
                "limited" is available.
            reward_weights : dict
                Dictionary of weight values to be used in reward calculation.
                If None, will use DEFAULT_REWARD_WEIGHTS.
                Each weight will be multiplied by the corresponding observation
                value, and the totals summed to get the whole reward.
            termination_steps : int
                Number of steps to execute in the environment before
                termination.
        """
        self.render_mode = render_mode
        self.window = None
        self.clock = None

        self.step_num = 0
        self.termination_steps = termination_steps

        if self.passenger_generator is not None:
            self.passenger_generator = passenger_generator
        else:
            pa_params = PassengerArrivals.generate_default_params(
                num_elevators, num_floors
            )
            self.passenger_generator = PassengerArrivals(**pa_params)

        self._generate_building(num_floors, num_elevators, max_queue,
                                elevator_params)
        self.observation_type = observation_type

        if reward_weights is None:
            self.reward_weights = DEFAULT_REWARD_WEIGHTS
        else:
            self.reward_weights = reward_weights

        # Set action space to all available actions for each elevator
        self.action_space = spaces.MultiDiscrete(
            [len(Action) for _ in num_elevators]
        )

        if observation_type == 'limited':
            self.observation_space = spaces.Dict(
                elevator_buttons=spaces.MultiBinary(
                    [num_elevators, num_floors]
                ),
                queue_buttons=spaces.MultiBinary([num_floors, 2]),
                elevator_floors=spaces.MultiDiscrete(
                    [num_floors for _ in range(num_elevators)]
                )
            )
        else:
            raise Exception("This observation type is not implemented yet.")

    def reset(self, seed=None):
        """
        Resets the environment, including the building, elevator and
        passengers.

        Args:
            seed : int
                Random seed to provide to the gym environment
        """
        # TODO: look into if we need options or not?
        super().reset(seed=seed)
        self.building.reset()
        self.step_num = 0

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def _generate_building(self, num_floors, num_elevators, max_queue,
                           elevator_params):
        """
        Create a Building object that the environment will be acting upon.

        Args:
           num_floors : int
                Number of floors in the building
            num_elevators : int
                Number of elevators in the building
            max_queue : int
                Total number of passengers that will join an up or down queue
                before the next potential Passenger
            elevator_params : dict
                Dictionary with the elevator_capacities, elevator_start_floors,
                and elevator_bounds from the Building constructor. Please see
                constructor definition for additional details on definition.
        """
        elevator_start_floors = None
        if 'elevator_start_floors' in elevator_params:
            elevator_start_floors = elevator_params['elevator_start_floors']

        elevator_bounds = None
        if 'elevator_bounds' in elevator_params:
            elevator_bounds = elevator_params['elevator_bounds']

        elevator_capacities = elevator_params['elevator_capacities']

        self.building = Building(
            num_floors, num_elevators, max_queue, elevator_capacities,
            elevator_start_floors, elevator_bounds
        )

    def step(self, action):
        """
        Execute an action composed of individual elevator actions.
        Calculate the reward and return status of the environment.

        Returns:
            observation : spaces.Dict
            reward : float
            terminated : bool
            truncated : bool
            info : dict
        """
        arrived_passengers = self.passenger_generator.generate_passengers()
        self.building.execute_step(arrived_passengers, action)
        self.step_num += 1

        terminated = self.step_num > self.termination_steps
        reward = self.calculate_reward()
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info

    def calculate_reward(self):
        """
        Calculate the environment reward for the current state with the
        current reward weights.

        Returns: float
        """
        reward_components = self.building.get_reward_components()

        reward_components['deboarding_passengers'] = len(
            reward_components['deboarding_passengers']
        )
        reward_components['rejected_queue_passengers'] = len(
            reward_components['rejected_queue_passengers']
        )
        reward_components['reached_max_wait_passengers'] = len(
            reward_components['reached_max_wait_passengers']
        )

        total_reward = 0.0

        for component, value in reward_components.items():
            total_reward += self.reward_weights[component] * value

        return total_reward

    def _get_obs(self):
        """
        Given the observation type, return either the limited or full
        observation of the environment space.

        The limited environment only inclues the elvator buttons, queue
        buttons, and elevator floors.

        Currently the full observation is not yet implemented.

        Returns: dict
        """
        if self.observation_type == 'limited':
            return self.building.get_observation_limited()

        # Should have thrown error when creating so we don't reach this yet
        return None

    def _get_info(self):
        """
        Get the information we use to calculate reward components, but split
        out so we can track performance for each component.

        Returns: dict
        """
        return self.building.get_reward_components()

    def render(self):
        # TODO: this
        pass

    def _render_frame():
        # TODO: this
        pass

    def close(self):
        if self.window is not None:
            # TODO: implement pygame visual
            pass
