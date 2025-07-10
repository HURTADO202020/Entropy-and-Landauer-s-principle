import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from matplotlib.animation import PillowWriter

class Particle:
    def __init__(self, x, y, velocity_x, velocity_y, cut_velocity):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.cut_velocity = cut_velocity
        self.processed = False  # Track if particle has been processed at barrier

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

        # Reset processed flag when leaving barrier region
        if not (0.95 < self.x < 1.05):
            self.processed = False

    def is_fast(self):
        return np.abs(self.velocity_x) > self.cut_velocity

    def get_colour(self):
        return 'red' if self.is_fast() else 'blue'

    def get_position(self):
        return (self.x, self.y)

class MaxwellDemon:
    def __init__(self, n_particles=50, cut_velocity=2.0):
        self.n_particles = n_particles
        self.cut_velocity = cut_velocity
        self.memory_bits = []
        self.energy_cost = []  # Track energy cost history
        self.bit_history = []  # Track bit count history
        self.landauer_constant = np.log(2)  # kT ln2 in arbitrary units (kT=1)

        # Create particles with 2D velocities
        self.particles = [
            Particle(
                x=np.random.uniform(0.2, 2.0),
                y=np.random.uniform(-0.8, 0.8),
                velocity_x=np.random.normal(0, 1.5),
                velocity_y=np.random.normal(0, 1.5),
                cut_velocity=cut_velocity
            )
            for _ in range(n_particles)
        ]

        # Setup figure with two subplots
        self.fig = plt.figure(figsize=(14, 6))
        self.ax_sim = self.fig.add_subplot(121)  # Simulation plot
        self.ax_energy = self.fig.add_subplot(122)  # Energy cost plot

        # Simulation plot setup
        self.ax_sim.set_xlim(0, 2)
        self.ax_sim.set_ylim(-1, 1)
        self.ax_sim.set_title("Maxwell's Demon Simulation")
        self.ax_sim.axvline(1, color='black', linestyle='--')
        self.ax_sim.axhline(1, color='gray', linestyle='-', alpha=0.3)
        self.ax_sim.axhline(-1, color='gray', linestyle='-', alpha=0.3)

        # Trapdoor setup
        self.trapdoor_width = 0.05
        self.trapdoor_height = 0.5
        self.trapdoor_x = 1 - self.trapdoor_width / 2
        self.trapdoor_closed_y = -0.9
        self.trapdoor = Rectangle(
            (self.trapdoor_x, self.trapdoor_closed_y),
            self.trapdoor_width,
            self.trapdoor_height,
            color='red',
            alpha=0.2
        )
        self.ax_sim.add_patch(self.trapdoor)

        # Draw initial particles
        self.scatter = self.ax_sim.scatter(
            [p.x for p in self.particles],
            [p.y for p in self.particles],
            c=[p.get_colour() for p in self.particles],
            alpha=0.7
        )

        # Info text
        self.info_text = self.ax_sim.text(0.02, 0.88, "", transform=self.ax_sim.transAxes, fontsize=10)

        # Energy cost plot setup
        self.ax_energy.set_title("Landauer Principle: Memory Energy Cost")
        self.ax_energy.set_xlabel("Bits of Information")
        self.ax_energy.set_ylabel("Energy Cost (kT ln2)")
        self.ax_energy.grid(True)
        self.energy_line, = self.ax_energy.plot([], [], 'r-', label="Cumulative Energy Cost")
        self.ax_energy.legend()
        self.ax_energy.axhline(y=self.landauer_constant, color='gray', linestyle='--', alpha=0.5)
        self.ax_energy.text(5, self.landauer_constant+1, "Cost per bit = kT ln2", fontsize=9)

    def update(self, frame):
        trapdoor_open = False
        new_bits_added = 0  # Track how many new bits we add this frame

        for particle in self.particles:
            particle.move()

            # Only process particles that enter the barrier region and haven't been processed yet
            if 0.95 < particle.x < 1.05 and not particle.processed:
                particle.processed = True  # Mark as processed to prevent duplicate counting

                if particle.is_fast():  # Fast particle
                    if particle.velocity_x > 0.0:
                        particle.velocity_x *= -1  # Bounce back to left
                    else:  # velocity_x < 0.0
                        trapdoor_open = True  # Allow to continue to right
                        self.memory_bits.append(True)
                        new_bits_added += 1
                else:  # Slow particle
                    if particle.velocity_x > 0.0:
                        trapdoor_open = True  # Allow to continue to right
                        self.memory_bits.append(True)
                        new_bits_added += 1
                    else:  # velocity_x < 0.0
                        particle.velocity_x *= -1  # Bounce back to left

        # Update visualization
        self.scatter.set_offsets([p.get_position() for p in self.particles])
        self.scatter.set_color([p.get_colour() for p in self.particles])
        self.trapdoor.set_alpha(0.9 if trapdoor_open else 0.2)

        # Update info text
        self.info_text.set_text(
            f"Bits Lost: {len(self.memory_bits)} bits\n"
            f"Particles in A (<1): {sum(1 for p in self.particles if p.x < 1)}\n"
            f"Particles in B (≥1): {sum(1 for p in self.particles if p.x >= 1)}"
        )

        # Update energy cost plot if new bits were added
        if new_bits_added > 0:
            total_bits = len(self.memory_bits)
            energy_cost = total_bits * self.landauer_constant

            self.bit_history.append(total_bits)
            self.energy_cost.append(energy_cost)

            self.energy_line.set_data(self.bit_history, self.energy_cost)

            # Adjust plot limits if needed
            if total_bits > self.ax_energy.get_xlim()[1] * 0.8:
                self.ax_energy.set_xlim(0, total_bits * 1.2)
            if energy_cost > self.ax_energy.get_ylim()[1] * 0.8:
                self.ax_energy.set_ylim(0, energy_cost * 1.2)

        return self.scatter, self.trapdoor, self.info_text, self.energy_line

    def animate(self):
        gif_filename = "maxwell_demon_simulation.gif"
        ani = FuncAnimation(self.fig, self.update, frames=750, interval=75, blit=False)
        # Set up GIF writer with optimization options
        writer = PillowWriter(fps=20,
                             bitrate=1800,
                             metadata=dict(artist='Maxwell Demon Simulation'))

        print(f"Saving animation to {gif_filename}...")
        ani.save(gif_filename, writer=writer)
        print("Animation saved successfully!")
        ani = FuncAnimation(self.fig, self.update, frames=1000, interval=50, blit=False)
        #plt.tight_layout()
        plt.show()

# Create and run simulation
simulation = MaxwellDemon(n_particles=50, cut_velocity=2.0)
simulation.animate()
