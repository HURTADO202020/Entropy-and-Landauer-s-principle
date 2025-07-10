import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

class Particle:
    def __init__(self, x, y, velocity_x, velocity_y, cut_velocity):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.cut_velocity = cut_velocity

    def move(self):
        self.x += self.velocity_x * 0.01
        self.y += self.velocity_y * 0.01

        # Boundary bouncing (X-direction)
        if self.x < 0:
            self.x = 0
            self.velocity_x *= -1
        elif self.x > 2:
            self.x = 2
            self.velocity_x *= -1

        # Boundary bouncing (Y-direction)
        if self.y < -1:
            self.y = -1
            self.velocity_y *= -1
        elif self.y > 1:
            self.y = 1
            self.velocity_y *= -1

    def is_fast(self):
        return np.abs(self.velocity_x) > self.cut_velocity  # Only consider x-velocity for speed check

    def get_colour(self):
        return 'red' if self.is_fast() else 'blue'

    def get_position(self):
        return (self.x, self.y)

class MaxwellDemon:
    def __init__(self, n_particles=50, cut_velocity=2.0):
        self.n_particles = n_particles
        self.cut_velocity = cut_velocity
        self.memory_bits = []

        # Create particles with 2D velocities
        self.particles = [
            Particle(
                x=np.random.uniform(0.0, 2.0),
                y=np.random.uniform(-0.8, 0.8),
                velocity_x=np.random.normal(0, 1.5),
                velocity_y=np.random.normal(0, 1.5),
                cut_velocity=cut_velocity
            )
            for _ in range(n_particles)
        ]

        # Figure setup
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.ax.set_xlim(0, 2)
        self.ax.set_ylim(-1, 1)
        self.ax.set_title("Maxwell's Demon (2D Version)")
        self.ax.axvline(1, color='black', linestyle='--')

        # Add top/bottom boundaries to visualization
        self.ax.axhline(1, color='gray', linestyle='-', alpha=0.3)
        self.ax.axhline(-1, color='gray', linestyle='-', alpha=0.3)

        # Trapdoor setup (visual only - doesn't affect physics)
        self.trapdoor_width = 0.05
        self.trapdoor_height = 0.5
        self.trapdoor_x = 1 - self.trapdoor_width / 2
        self.trapdoor_closed_y = -0.9
        self.trapdoor_open_y = -0.5
        self.trapdoor = Rectangle(
            (self.trapdoor_x, self.trapdoor_closed_y),
            self.trapdoor_width,
            self.trapdoor_height,
            color='red',
            alpha=0.2
        )
        self.ax.add_patch(self.trapdoor)

        # Draw initial particles
        self.scatter = self.ax.scatter(
            [p.x for p in self.particles],
            [p.y for p in self.particles],
            c=[p.get_colour() for p in self.particles],
            alpha=0.7
        )

        # Info text
        self.info_text = self.ax.text(0.02, 0.88, "", transform=self.ax.transAxes, fontsize=10)

    def update(self, frame):
        trapdoor_open = False

        for particle in self.particles:
            particle.move()

            # Demon's logic near x = 1 (ignores y-coordinate)
            if 0.95 < particle.x < 1.05:
                if particle.is_fast(): # Fast particle
                    if particle.velocity_x > 0.0:
                        particle.velocity_x *= -1  # Bounce
                    elif particle.velocity_x < 0.0:
                        trapdoor_open = True # Continue
                        self.memory_bits.append(True)
                else:
                    if particle.velocity_x > 0.0: # Slow particle
                        trapdoor_open = True # Continue
                        self.memory_bits.append(True)
                    elif particle.velocity_x < 0.0:
                        particle.velocity_x *= -1  # Bounce

        # Update visualization
        self.scatter.set_offsets([p.get_position() for p in self.particles])
        self.scatter.set_color([p.get_colour() for p in self.particles])

        # Update trapdoor (visual only)
        self.trapdoor.set_alpha(0.9 if trapdoor_open else 0.2)

        # Update info text
        self.info_text.set_text(
            f"Memory: {len(self.memory_bits)} bits\n"
            f"Particles in A (<1): {sum(1 for p in self.particles if p.x < 1)}\n"
            f"Particles in B (≥1): {sum(1 for p in self.particles if p.x >= 1)}"
        )

        return self.scatter, self.trapdoor, self.info_text

    def animate(self):
        ani = FuncAnimation(self.fig, self.update, frames=1000, interval=50, blit=False)
        plt.show()

# Create and run simulation
simulation = MaxwellDemon(n_particles=50, cut_velocity=2.0)
simulation.animate()
