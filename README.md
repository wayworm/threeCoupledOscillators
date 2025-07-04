## Spring-Coupled Oscillator Simulation (Pygame)

This Python script simulates a dynamic system of balls (oscillators) connected by invisible springs using Pygame. Each ball moves under the influence of spring forces and collisions, visualising principles of classical mechanics and numerical integration.

### Features

- Spring-Mass System: Balls interact via Hookean springs with configurable rest length and spring constant.
- Verlet Integration: Accurate, stable position and velocity updates using the Velocity Verlet algorithm.
- Collision Handling: Elastic collisions between balls and screen boundaries.
- Momentum Display: Real-time display of total momentum deviation from the initial state.
- Trails: Each ball leaves a fading trail of its past positions.

### How It Works

Balls are initialized with random positions, velocities, and radii.

Springs connect all unique pairs of balls, exerting forces based on displacement from rest length.

The simulation updates:

- Resetting accelerations
- Applying spring forces
- Updating positions (Verlet)
- Resolving collisions
- Finalizing velocities (Verlet)

Momentum deviation is calculated and rendered.

### Requirements

    Python 3
    pygame
    numpy


Usage

Run the script with:

python <filename>.py

Use the display window to observe the spring-coupled system evolve over time.
