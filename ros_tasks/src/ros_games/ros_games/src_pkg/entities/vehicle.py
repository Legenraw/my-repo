import numpy as np
from ros_games.src_pkg.utils.physics_helpers import compute_drag_force, compute_angular_drag, compute_current_force


class Vehicle:
    """Physics simulation for underwater vehicle.

    Handles vehicle dynamics including thrust, drag, and environmental forces.
    """

    def __init__(self, config, current_time: float = 0.0):
        self.config = config
        self.position = np.array([0.0, 0.0])
        self.orientation = 0.0
        self.velocity = np.array([0.0, 0.0])
        self.angular_velocity = 0.0
        self.acceleration = np.array([0.0, 0.0])
        self.angular_acceleration = 0.0

        # Vehicle properties
        self.mass = config.submarine_parameters['mass']
        self.moment_of_inertia = config.submarine_parameters['moment_of_inertia']
        self.drag_area = config.submarine_parameters.get('drag_area', 0.5)

        # Velocity limits
        self.max_velocity = config.submarine_parameters.get('max_velocity', 50.0)
        self.max_angular_velocity = config.submarine_parameters.get('max_angular_velocity', 1.0)

        # Physics parameters
        self.water_density = config.physics_constants['water_density']
        self.drag_coefficient = config.physics_constants['drag_coefficient']
        self.angular_drag_coefficient = config.physics_constants.get('angular_drag_coefficient', 0.1)

        # Current/disturbance parameters
        self.enable_currents = config.physics_constants.get('enable_currents', False)
        self.current_strength = config.physics_constants.get('current_strength', 0.0)
        self.current_direction = np.array(config.physics_constants.get('current_direction', [1.0, 0.0]))
        self.turbulence_enabled = config.physics_constants.get('turbulence_enabled', False)

        # Time tracking for current calculation
        self.current_time = current_time

    def apply_force(self, force: np.ndarray):
        """Apply a force to the vehicle."""
        self.acceleration += force / self.mass

    def apply_torque(self, torque: float):
        """Apply a torque to the vehicle."""
        self.angular_acceleration += torque / self.moment_of_inertia

    def update(self, dt: float):
        """Update vehicle physics for one timestep.

        Args:
            dt: Time step in seconds
        """
        # Apply drag forces
        drag_force = compute_drag_force(
            self.velocity,
            self.water_density,
            self.drag_coefficient,
            self.drag_area
        )
        self.apply_force(drag_force)

        # Apply angular drag
        angular_drag_torque = compute_angular_drag(
            self.angular_velocity,
            self.angular_drag_coefficient
        )
        self.apply_torque(angular_drag_torque)

        # Apply water currents/disturbances
        if self.enable_currents and self.current_strength > 0:
            current_force = compute_current_force(
                self.position,
                self.current_time,
                self.current_strength,
                self.current_direction,
                self.turbulence_enabled
            )
            self.apply_force(current_force)

        # Update velocities from acceleration
        self.velocity += self.acceleration * dt
        self.angular_velocity += self.angular_acceleration * dt

        # Cap linear velocity
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_velocity:
            self.velocity = (self.velocity / speed) * self.max_velocity

        # Cap angular velocity
        self.angular_velocity = np.clip(
            self.angular_velocity,
            -self.max_angular_velocity,
            self.max_angular_velocity
        )

        # Update position and orientation
        self.position += self.velocity * dt
        self.orientation += self.angular_velocity * dt

        # Normalize orientation to [-π, π]
        self.orientation = np.arctan2(np.sin(self.orientation), np.cos(self.orientation))

        # Update time
        self.current_time += dt

        # Reset accelerations for next frame
        self.acceleration = np.array([0.0, 0.0])
        self.angular_acceleration = 0.0

    def get_speed(self) -> float:
        """Get current speed magnitude."""
        return np.linalg.norm(self.velocity)
