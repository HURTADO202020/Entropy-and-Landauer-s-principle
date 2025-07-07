import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

# Número de partículas
n_particles = 20

# Posiciones iniciales y velocidades
positions = np.random.uniform(0.0, 2.0, n_particles)
velocities = np.random.normal(0.0, 4.0, n_particles)
y_positions = np.random.uniform(-0.8, 0.8, n_particles)

memory_bits = []

# Crear la figura y ejes
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_xlim(0, 2)
ax.set_ylim(-1, 1)
ax.set_title("Demonio de Maxwell")
ax.axvline(1, color='black', linestyle='--')  # Puerta en x=1

# Puerta (trampilla)
trapdoor = Rectangle((1, -0.9), 0.1, 0.1, color='red', alpha=0.2)
ax.add_patch(trapdoor)

# Dibujar partículas
particles = ax.scatter(positions, y_positions, c=np.where(velocities > 0, 'red', 'blue'), alpha=0.7)

# Texto informativo
info_text = ax.text(0.02, 0.9, "", transform=ax.transAxes, fontsize=10)

def update(frame):
    global positions, velocities, memory_bits

    trapdoor_open = False

    for i in range(n_particles):
        # Movimiento simple
        positions[i] += velocities[i]

        # Rebote en los bordes
        if positions[i] < 0 or positions[i] > 2:
            velocities[i] *= -1

        # Demonio abre la trampilla: si está a la izquierda y va a la derecha
        if 0.98 < positions[i] < 1.0 and 2 < velocities[i] < 4:
            trapdoor_open = True
            memory_bits.append(True)  # Se almacena la decisión
            # Se deja pasar, no se rebota

    # Actualizar colores y posiciones
    particles.set_offsets(np.column_stack((positions, y_positions)))
    particles.set_color(np.where(velocities > 0, 'red', 'blue'))

    # Cambiar opacidad de la trampilla
    trapdoor.set_alpha(0.9 if trapdoor_open else 0.2)

    # Actualizar texto
    info_text.set_text(f"Memoria: {len(memory_bits)} bits\n"
                       f"Partículas en A (<1): {np.sum(positions < 1)}\n"
                       f"Partículas en B (>=1): {np.sum(positions >= 1)}")

    return particles, trapdoor, info_text

# Crear animación
ani = FuncAnimation(fig, update, frames=10000, interval=50, blit=False)
plt.show()

