import numpy as np
from typing import Tuple


class Obstacle:
    """Represents a circular obstacle in the environment."""

    def __init__(self, position: np.ndarray, radius: float, obstacle_id: int = 0):
        """Initialize obstacle.

        Args:
            position: Obstacle center position [x, y]
            radius: Obstacle radius
            obstacle_id: Unique identifier for this obstacle
        """
        self.position = position.copy()
        self.radius = radius
        self.id = obstacle_id

    def check_collision(self, point: np.ndarray, point_radius: float = 0.0) -> bool:
        """Check if a point (with optional radius) collides with obstacle.

        Args:
            point: Point position [x, y]
            point_radius: Radius of the point (e.g., vehicle radius)

        Returns:
            True if collision detected
        """
        distance = np.linalg.norm(point - self.position)
        return distance <= (self.radius + point_radius)

    def distance_to(self, point: np.ndarray) -> float:
        """Calculate distance from point to obstacle surface.

        Args:
            point: Point position [x, y]

        Returns:
            Distance to obstacle surface (negative if inside)
        """
        distance_to_center = np.linalg.norm(point - self.position)
        return distance_to_center - self.radius

    def to_dict(self) -> dict:
        """Convert obstacle to dictionary for logging."""
        return {
            "id": self.id,
            "position": self.position.tolist(),
            "radius": float(self.radius)
        }
