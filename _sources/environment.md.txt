# Environment

This environment simulates a turn-based, multi-decision elevator control system to carry passengers from their arrival floors to their destination floors. We say multi-decision rather than multi-agent because we have a single agent making decisions for every available elevator.

## Environment Components

The environment creates and manages several underlying data structures that define the state and affect it through actions. 

### Passenger

The base component of the environment is the `Passenger`. Each passenger arrives at a floor in the building, and has a destination floor they want to get through, that is not their arrival floor. Based on whether their destination floor is above or below their arrival floor, they will try to join the corresponding elevator queue on that floor. 

If the queue they are trying to join is full, they will not join any queue, and their rejection will be tracked and included in the reward function. 

When they arrive in the building, they track the timestep at which they arrived, as well as setting both a wait time and overall age to zero. The wait time tracks how many steps they spent in an elevator queue and it will not be incremented if they enter an elevator. The age increases at every timestep regardless of location. 

Each passenger has a maximum amount of steps they will wait in a queue before leaving the queue, at which point their departure will be noted and included in the reward function.

### Passenger Arrival Generator

The passenger arrival generator's function is to generate new passengers at the beginning every time step in the environment, and it is comprised of two main components:

- Floor arrival rates
  - We use the [Poisson distribution](https://en.wikipedia.org/wiki/Poisson_distribution) to model the random arrival of passengers on each floor.
  - The distribution is defined by a single lambda value, and the arrival generator holds a lambda value for each floor.
  - Low lambda values may have zero arrivals for a floor on a given turn, while higher values may have from zero to multiple.
- Floor destination rates
  - When passengers are created and are defined as arriving on a specific floor, we want to randomly determine what their destination floor is.
  - Each floor has a list of probabilities for the number of floors in the building that meets the following conditions:
    - The sum of all probabilities must sum to one.
    - The arrival floor probability must be set to zero since passengers will never want to take an elevator to the same floor.

#### Default Parameters

While this is a flexible system, we have implemented a default case where the arrival rate of the ground floor is highest, while all other floors have a low arrival rate. Correspondingly, the ground floor has a random chance to go to any non-ground floor, while the non-ground floors most often want to go to the ground floor with a small chance to head to another non-ground floor.

Please see the `arrivals.PassengerArrivals.generate_default_params` function for details.

### Elevator

Each building has at least one elevator, and each elevator's function is (obviously) to pick up passengers from queues and drop them off on their destination floors. All actions are executed by the elevators in the system, whereas the passengers are just part of the state and reward function.

The elevators have a minimum and maximum floor range that they can visit, and they have a maximum number of passengers they can hold at one time. It knows what floor it is currently on and what passengers are riding it. 

The default parameters for elevators set their floor range to be the entire building, but the user can modify this to configure non-standard elevator arrangements where some only service the bottom part of the building and others the top.

### Building

The building is a wrapper that holds the elevators and elevator waiting queues, and it manages passenger arrivals, executes actions, steps the environment forwards, manages observations and reward function components, and handles the small details such as passenger queue rejections, aging forwards, etc. Ultimately, this class holds most of the main logic surrounding state, and the environment is just a wrapper around this. 

## Action Space

There are 6 actions that an elevator can take:
    
0. Do nothing and remain at the current floor.
1. Attempt to move up a floor. This does nothing if at the
    elevator's maximum floor.
2. Attempt to move down a floor. This does nothing if at the
    elevator's minimum floor.
3. Load as many passengers will fit in the remaining elevator
    capacity from the current floor that are in the up queue
    starting from the first arrived passengers onward.
4. Load as many passengers will fit in the remaining elevator
    capacity from the current floor that are in the down queue
    starting from the first arrived passengers onward.
5. Unload any passengers that have their destination floor as
    the elevator's current floor.

These are implemented in the gymnasium [`MultiDisrete`](https://gymnasium.farama.org/api/spaces/fundamental/#multidiscrete) space, with one action to be passed into each step for each elevator in the building.

## Observation Space

The observation space is currently a WIP, and, though we have multiple options for observation spaces planned, only the `limited` observation space is currently implemented.

The limited observation space is meant to mimic a realistic elevator environment, where only available data to an elevator system are what buttons are pressed on each floor for the queues, as well as the destination floor buttons within the elevators. We don't know any of the passengers' true destinations in the queue or how many passengers pressed the destination buttons. Lastly, the elevators know what floor they are on. 

The raw observation space is implemented as a [`Dict`](https://gymnasium.farama.org/api/spaces/composite/#dict) space with [`MultiBinary`](https://gymnasium.farama.org/api/spaces/fundamental/#multibinary) spaces for the elevator buttons and queue buttons, with a `MultiDiscrete` space for the elevator locations.

Unfortunately, not all learning algorithms are built to work with the `Dict` space, so we have a `flatten_space` parameter in the environment that takes all of the `Dict` components above and turns it into a large `MultiBinary` space equal to length (`num_floors x num_elevators`) + (`num_floors x 2`) + (`num_floors x num_elevators`) corresponding to the elevator buttons, elevator queues, and elevator locations respectively. This should be compatible with common tools such as [stable-baselines](https://stable-baselines3.readthedocs.io/en/master/).

## Environment Step

The environment step function does the usual things one would expect from a gymnasium environment, but here are the details about what happens to the underlying component states:

1. Generate new passengers with the passenger arrival generator
2. Remove passengers in elevator queues that have reached their maximum wait time
3. Attempt to add new passengers to elevator queues and tracking failed joins from maximum size queues
4. Execute each action for each elevator in the building in the order they were provided; the first elevator in the building elevators list executes the first action passed into the step function
5. Increment passenger wait and age properties
6. Increment the environment step number
7. Return observation space, reward and termination status

## Reward Function

The reward function applies a dictionary of weights to multiplied by the corresponding attributes returned from the building. There are positive and negative components to the reward function that should contribute positively and negatively to the final reward value respectively.

Below, the components are listed in order from highest to lowest weights using the default parameters, although the user can provide any of their own weights to the environment.

### Positive Components

- The count of assengers unloaded to their destination floor
- The count of passengers that were moved toward their destination floor while in an elevator

### Negative Components

- The count of passengers that tried to join a full queue and were denied
- The count of passengers that reached their maximum wait time and left the queue
- The count of passengers that were moved away from their destination floor while in an elevator
- The count of passengers in an elevator
- The count of passengers in a queue

## Advanced Usage

While this environment is designed to work without any additional definition inputs from the user, it can be modified by the user in a number of ways to test alternative goals and building layout scenarios:

- Simulating a workout gym/restaurant on an upper floor by increasing its destination probability and arrival probabilities
- Restricting certain elevators to only lower or upper floors to focus on localized transport for buildings with a lot of non-ground floor travel.
- Prioritizing getting passengers onto elevators at the cost of going in the opposite direction for a floor or two rather than having them continue to wait and max out queues.

This is a well-researched subject area, but as buildings become larger and more complicated, we believe that reinforcement learning may be a way to test novel configurations and automatically generate policies rather than involve lengthy manual implementations.

## Limitations

We have some large assumptions around the equivalence of various actions' time for execution which make it unrealistic for a real elevator environment, but which speed up the environment's execution time but not having to learn actions for every single second. 

Additionally, the visual rendering part of the environment is not yet implemented.