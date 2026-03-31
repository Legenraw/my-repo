import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


class Logger:
    """Two-level logging system for game episodes.

    Provides:
    1. Frame-level telemetry logs (.txt) - detailed vehicle state every frame
    2. Event logs (.json) - high-level events and episode summary
    """

    def __init__(self, log_dir: str = "./logs", episode_id: Optional[str] = None):
        """Initialize logger.

        Args:
            log_dir: Base directory for logs
            episode_id: Episode identifier (auto-generated if None)
        """
        self.log_dir = log_dir

        # Auto-generate episode ID if not provided
        if episode_id is None:
            episode_id = self._get_next_episode_id()
        self.episode_id = episode_id

        # Create episode directory
        self.episode_dir = os.path.join(log_dir, f"episode_{episode_id}")
        os.makedirs(self.episode_dir, exist_ok=True)

        # File paths
        self.telemetry_path = os.path.join(self.episode_dir, "telemetry.txt")
        self.events_path = os.path.join(self.episode_dir, "events.json")

        # Initialize telemetry file
        self.telemetry_file = open(self.telemetry_path, 'w')

        # Initialize events structure
        self.events_data = {
            "episode_id": episode_id,
            "game_mode": None,
            "start_time": datetime.now().isoformat(),
            "config": {},
            "events": [],
            "summary": {}
        }

        self.enabled = True

    def _get_next_episode_id(self) -> str:
        """Get next available episode ID by checking existing directories."""
        if not os.path.exists(self.log_dir):
            return "001"

        existing = [d for d in os.listdir(self.log_dir) if d.startswith("episode_")]
        if not existing:
            return "001"

        # Extract episode numbers
        numbers = []
        for dirname in existing:
            try:
                num = int(dirname.split("_")[1])
                numbers.append(num)
            except (IndexError, ValueError):
                continue

        if not numbers:
            return "001"

        next_num = max(numbers) + 1
        return f"{next_num:03d}"

    def set_game_mode(self, game_mode: str):
        """Set the game mode for this episode."""
        self.events_data["game_mode"] = game_mode

    def set_config(self, config: Dict[str, Any]):
        """Store configuration for this episode."""
        self.events_data["config"] = config

    def log_telemetry(self, step: int, time: float, data: Dict[str, Any]):
        """Log frame-level telemetry data.

        Args:
            step: Current step number
            time: Current time in seconds
            data: Dictionary with telemetry data (position, velocity, etc.)
        """
        if not self.enabled:
            return

        # Format: Step X | Time: X.XXXs | Pos: (x, y) | Vel: (vx, vy) | ...
        line_parts = [
            f"Step {step}",
            f"Time: {time:.3f}s",
            f"Pos: ({data.get('pos_x', 0):.1f}, {data.get('pos_y', 0):.1f})",
            f"Vel: ({data.get('vel_x', 0):.1f}, {data.get('vel_y', 0):.1f})",
            f"Orient: {data.get('orientation', 0):.2f} rad",
            f"AngVel: {data.get('angular_velocity', 0):.2f}",
            f"Speed: {data.get('speed', 0):.1f}"
        ]

        # Add optional game-specific data
        if 'distance_to_target' in data:
            line_parts.append(f"DistToTarget: {data['distance_to_target']:.1f}")

        if 'colliding' in data:
            line_parts.append(f"Colliding: {data['colliding']}")
            if 'nearest_obstacle' in data:
                line_parts.append(f"NearestObstacle: {data['nearest_obstacle']:.1f}")

        if 'score' in data:
            line_parts.append(f"Score: {data['score']}")
            if 'active_shapes' in data:
                line_parts.append(f"ActiveShapes: {data['active_shapes']}")

        line = " | ".join(line_parts) + "\n"
        self.telemetry_file.write(line)

    def log_event(self, step: int, time: float, event_type: str, event_data: Dict[str, Any]):
        """Log a high-level event.

        Args:
            step: Current step number
            time: Current time in seconds
            event_type: Type of event (e.g., "episode_start", "collision", etc.)
            event_data: Additional event-specific data
        """
        if not self.enabled:
            return

        event = {
            "step": step,
            "time": time,
            "type": event_type,
            "data": event_data
        }
        self.events_data["events"].append(event)

    def set_summary(self, summary: Dict[str, Any]):
        """Set episode summary data."""
        self.events_data["summary"] = summary

    def close(self):
        """Close log files and write final event log."""
        if not self.enabled:
            return

        # Close telemetry file
        self.telemetry_file.close()

        # Write events JSON
        with open(self.events_path, 'w') as f:
            json.dump(self.events_data, f, indent=2)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
