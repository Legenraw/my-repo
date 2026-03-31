import numpy as np


def normalize(vector: np.ndarray) -> np.ndarray:
    """Normalize a vector to unit length."""
    norm = np.linalg.norm(vector)
    return vector / norm if norm > 0 else vector


def rotate_vector(vector, angle):
    """Rotate a 2D vector by an angle (in radians)."""
    c, s = np.cos(angle), np.sin(angle)
    return np.array([c * vector[0] - s * vector[1],
                     s * vector[0] + c * vector[1]])


def compute_drag_force(velocity: np.ndarray, water_density: float,
                        drag_coefficient: float, drag_area: float) -> np.ndarray:
    """Compute quadratic drag force on vehicle.

    Uses the drag equation: F_drag = -0.5 * ρ * v² * C_d * A * v̂

    Args:
        velocity: Velocity vector [vx, vy]
        water_density: Density of water (kg/m³)
        drag_coefficient: Drag coefficient (dimensionless)
        drag_area: Cross-sectional area (m²)

    Returns:
        Drag force vector opposing motion
    """
    speed = np.linalg.norm(velocity)

    if speed < 0.01:  # Avoid division by zero
        return np.array([0.0, 0.0])

    # Direction opposite to velocity
    direction = -velocity / speed

    # Quadratic drag magnitude
    drag_magnitude = 0.5 * water_density * speed * speed * drag_coefficient * drag_area

    return drag_magnitude * direction


def compute_angular_drag(angular_velocity: float, angular_drag_coefficient: float) -> float:
    """Compute angular drag (damping torque).

    Args:
        angular_velocity: Angular velocity (rad/s)
        angular_drag_coefficient: Angular drag coefficient

    Returns:
        Damping torque opposing rotation
    """
    # Quadratic angular drag
    if abs(angular_velocity) < 0.01:
        return 0.0

    direction = -np.sign(angular_velocity)
    magnitude = angular_drag_coefficient * angular_velocity * angular_velocity
    return direction * magnitude


def compute_current_force(position: np.ndarray, time: float,
                          current_strength: float,
                          current_direction: np.ndarray,
                          turbulence_enabled: bool = False) -> np.ndarray:
    """Compute water current force acting on vehicle.

    Args:
        position: Vehicle position [x, y]
        time: Current simulation time
        current_strength: Base strength of current
        current_direction: Direction vector of current flow [x, y]
        turbulence_enabled: Whether to add turbulent disturbances

    Returns:
        Force vector from water current
    """
    # Normalize direction
    direction = normalize(current_direction)

    # Base current force
    base_force = current_strength * direction

    if turbulence_enabled:
        # Add spatial and temporal variation
        # Use position and time for deterministic but varying turbulence
        spatial_freq = 0.01  # Spatial frequency of turbulence
        temporal_freq = 0.5  # Temporal frequency

        turbulence_x = np.sin(position[0] * spatial_freq + time * temporal_freq) * 0.3
        turbulence_y = np.cos(position[1] * spatial_freq + time * temporal_freq * 1.3) * 0.3

        turbulence = np.array([turbulence_x, turbulence_y]) * current_strength

        return base_force + turbulence

    return base_force

