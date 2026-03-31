import numpy as np
from typing import Optional


class ImageData:
    """Represents an image from a dataset displayed in the environment for Game 4."""

    def __init__(self,
                 image: np.ndarray,
                 label: int,
                 position: np.ndarray,
                 display_size: tuple,
                 spawn_time: float,
                 duration: float,
                 image_id: str):
        """Initialize image data.

        Args:
            image: Image array (grayscale or RGB)
            label: True label/class of the image
            position: Display position [x, y] (center)
            display_size: Size to display image (width, height)
            spawn_time: Time when image was spawned
            duration: How long image remains visible
            image_id: Unique identifier
        """
        self.image = image.copy()
        self.label = int(label)
        self.position = position.copy()
        self.display_size = display_size
        self.spawn_time = spawn_time
        self.duration = duration
        self.expires_at = spawn_time + duration
        self.image_id = image_id

        # Track if this image has been correctly identified
        self.identified = False

    def is_expired(self, current_time: float) -> bool:
        """Check if image has expired.

        Args:
            current_time: Current game time

        Returns:
            True if image should be removed
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
        """Check if a point is inside the image bounds.

        Args:
            point: Point position [x, y]

        Returns:
            True if point is inside image
        """
        half_width = self.display_size[0] / 2
        half_height = self.display_size[1] / 2

        dx = abs(point[0] - self.position[0])
        dy = abs(point[1] - self.position[1])

        return dx <= half_width and dy <= half_height

    def to_dict(self) -> dict:
        """Convert image data to dictionary for logging."""
        return {
            "id": self.image_id,
            "label": self.label,
            "position": self.position.tolist(),
            "display_size": self.display_size,
            "spawn_time": float(self.spawn_time),
            "expires_at": float(self.expires_at),
            "identified": self.identified
        }
