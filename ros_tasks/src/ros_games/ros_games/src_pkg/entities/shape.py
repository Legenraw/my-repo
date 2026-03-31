import numpy as np
from typing import Tuple


class Shape:
    """Represents a colored shape in the environment for Game 3."""

    def __init__(self,
                 shape_type: str,
                 color_name: str,
                 color_rgb: Tuple[int, int, int],
                 position: np.ndarray,
                 size: float,
                 spawn_time: float,
                 duration: float,
                 shape_id: str):
        """Initialize shape.

        Args:
            shape_type: Type of shape ("circle", "square", "triangle")
            color_name: Name of color ("red", "blue", "green", etc.)
            color_rgb: RGB tuple (r, g, b)
            position: Shape center position [x, y]
            size: Shape size (radius for circle, side length for others)
            spawn_time: Time when shape was spawned
            duration: How long shape remains visible
            shape_id: Unique identifier
        """
        self.shape_type = shape_type
        self.color_name = color_name
        self.color_rgb = color_rgb
        self.position = position.copy()
        self.size = size
        self.spawn_time = spawn_time
        self.duration = duration
        self.expires_at = spawn_time + duration
        self.shape_id = shape_id

    def is_expired(self, current_time: float) -> bool:
        """Check if shape has expired.

        Args:
            current_time: Current game time

        Returns:
            True if shape should be removed
        """
        return current_time >= self.expires_at

    def time_remaining(self, current_time: float) -> float:
        """Get time remaining before expiration.

        Args:
            current_time: Current game time

        Returns:
            Time remaining in seconds (negative if expired)
        """
        return self.expires_at - current_time

    def contains_point(self, point: np.ndarray) -> bool:
        """Check if a point is inside the shape.

        Args:
            point: Point position [x, y]

        Returns:
            True if point is inside shape
        """
        if self.shape_type == "circle":
            distance = np.linalg.norm(point - self.position)
            return distance <= self.size
        elif self.shape_type == "square":
            # Square bounding box
            dx = abs(point[0] - self.position[0])
            dy = abs(point[1] - self.position[1])
            return dx <= self.size / 2 and dy <= self.size / 2
        elif self.shape_type == "triangle":
            # Simple bounding circle approximation
            distance = np.linalg.norm(point - self.position)
            return distance <= self.size
        else:
            return False

    def to_dict(self) -> dict:
        """Convert shape to dictionary for logging."""
        return {
            "id": self.shape_id,
            "type": self.shape_type,
            "color": self.color_name,
            "position": self.position.tolist(),
            "size": float(self.size),
            "spawn_time": float(self.spawn_time),
            "expires_at": float(self.expires_at)
        }
