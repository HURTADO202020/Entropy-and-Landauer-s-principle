import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

# Número de partículas
n_particles = 20

# Posiciones iniciales y velocidades
positions = np.random.uniform(0.0, 2.0, n_particles)
velocities = np.random.normal(0.0, 2.5, n_particles)
y_positions = np.random.uniform(-0.8, 0.8, n_particles)

# Memoria del demonio
memory_bits = []

# Crear figura y ejes
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_xlim(0, 2)
ax.set_ylim(-1, 1)
ax.set_title("Demonio de Maxwell")
ax.axvline(1, color='black', linestyle='--')  # Línea divisoria

# Trampilla
trapdoor_width = 0.05
trapdoor_height = 0.1
trapdoor_x = 1 - trapdoor_width / 2
trapdoor_closed_y = -0.9
trapdoor_open_y = -0.5  # Para visualización
trapdoor = Rectangle((trapdoor_x, trapdoor_closed_y), trapdoor_width, trapdoor_height, color='red', alpha=0.2)
ax.add_patch(trapdoor)

# Dibujar partículas (color por magnitud de velocidad)
particles = ax.scatter(positions, y_positions,
                       c=np.where(np.abs(velocities) > 2, 'red', 'blue'),
                       alpha=0.7)

# Texto informativo
info_text = ax.text(0.02, 0.9, "", transform=ax.transAxes, fontsize=10)

# Función de actualización
def update(frame):
    global positions, velocities, memory_bits
    trapdoor_open = False

    for i in range(n_particles):
        # Movimiento
        positions[i] += velocities[i] * 0.01

        # Rebote en bordes de la caja
        if positions[i] < 0:
            positions[i] = 0
            velocities[i] *= -1
        elif positions[i] > 2:
            positions[i] = 2
            velocities[i] *= -1

        # Lógica del demonio cerca de x = 1
        if 0.98 < positions[i] < 1.02:
            if np.abs(velocities[i]) != 2:  # Rápida o lenta
                trapdoor_open = True
                memory_bits.append(True)
                # Se permite el paso
            else:
                # Zona gris: velocidad = 2 → rebote
                velocities[i] *= -1

    # Actualizar posición y color de partículas
    particles.set_offsets(np.column_stack((positions, y_positions)))
    particles.set_color(np.where(np.abs(velocities) > 2, 'red', 'blue'))

    # Visualización de la trampilla (posición y transparencia)
    trapdoor.set_alpha(0.9 if trapdoor_open else 0.2)
    new_y = trapdoor_open_y if trapdoor_open else trapdoor_closed_y
    trapdoor.set_xy((trapdoor_x, new_y))

    # Actualizar texto
    info_text.set_text(f"Memoria: {len(memory_bits)} bits\n"
                       f"Partículas en A (<1): {np.sum(positions < 1)}\n"
                       f"Partículas en B (≥1): {np.sum(positions >= 1)}")

    return particles, trapdoor, info_text

# Animación
ani = FuncAnimation(fig, update, frames=1000, interval=50, blit=False)
plt.show()

