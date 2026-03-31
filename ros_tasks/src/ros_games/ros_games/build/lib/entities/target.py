import numpy as np


class Target:
    """Represents a target position for the vehicle to reach."""

    def __init__(self, position: np.ndarray, radius: float = 30.0):
        """Initialize target.

        Args:
            position: Target position [x, y]
            radius: Success radius (vehicle must get within this distance)
        """
        self.position = position.copy()
        self.radius = radius

    def is_reached(self, vehicle_position: np.ndarray) -> bool:
        """Check if vehicle has reached the target.

        Args:
            vehicle_position: Current vehicle position [x, y]

        Returns:
            True if vehicle is within success radius
        """
        distance = np.linalg.norm(vehicle_position - self.position)
        return distance <= self.radius

    def distance_to(self, vehicle_position: np.ndarray) -> float:
        """Calculate distance from vehicle to target.

        Args:
            vehicle_position: Current vehicle position [x, y]

        Returns:
            Euclidean distance to target
        """
        return np.linalg.norm(vehicle_position - self.position)
