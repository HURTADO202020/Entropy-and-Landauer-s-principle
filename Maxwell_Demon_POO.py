import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

class Particle:
    def __init__(self, x, y, velocity, cut_velocity):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.cut_velocity = cut_velocity
    
    def move(self):
        self.x += self.velocity * 0.01
        
        # Boundary bouncing
        if self.x < 0:
            self.x = 0
            self.velocity *= -1
        elif self.x > 2:
            self.x = 2
            self.velocity *= -1
    
    def is_fast(self):
        return np.abs(self.velocity) > self.cut_velocity
    
    def get_colour(self):
        return 'red' if self.is_fast() else 'blue'
    
    def get_position(self):
        return (self.x, self.y)

class MaxwellDemon:
    def __init__(self, n_particles=50, cut_velocity=2.0):
        self.n_particles = n_particles
        self.cut_velocity = cut_velocity
        self.memory_bits = []
        
        # Create particles
        self.particles = [
            Particle(
                x=np.random.uniform(0.0, 2.0),
                y=np.random.uniform(-0.8, 0.8),
                velocity=np.random.normal(0.5, 2.0*cut_velocity),
                cut_velocity=cut_velocity
            ) 
            for i in range(n_particles)
        ]
        
        # Figure setup
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.ax.set_xlim(0, 2)
        self.ax.set_ylim(-1, 1)
        self.ax.set_title("Maxwell's Demon (OOP)")
        self.ax.axvline(1, color='black', linestyle='--')
        
        # Trapdoor setup
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
        self.info_text = self.ax.text(0.02, 0.9, "", transform=self.ax.transAxes, fontsize=10)
    
    def update(self, frame):
        trapdoor_open = False
        
        for particle in self.particles:
            particle.move()
            
            # Demon's logic near x = 1
            if 0.95 < particle.x < 1.05:
                if particle.is_fast(): # Fast particle
                    if particle.velocity > 0.0:
                        particle.velocity *= -1  # Bounce
                    elif particle.velocity < 0.0:
                        trapdoor_open = True # Continue
                        self.memory_bits.append(True)
                else:
                    if particle.velocity > 0.0: # Slow particle
                        trapdoor_open = True # Continue
                        self.memory_bits.append(True)
                    elif particle.velocity < 0.0:
                        particle.velocity *= -1  # Bounce
        
        # Update visualization
        self.scatter.set_offsets([p.get_position() for p in self.particles])
        self.scatter.set_color([p.get_colour() for p in self.particles])
        
        # Update trapdoor
        self.trapdoor.set_alpha(0.9 if trapdoor_open else 0.2)
        new_y = self.trapdoor_open_y if trapdoor_open else self.trapdoor_closed_y
        self.trapdoor.set_xy((self.trapdoor_x, new_y))
        
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
