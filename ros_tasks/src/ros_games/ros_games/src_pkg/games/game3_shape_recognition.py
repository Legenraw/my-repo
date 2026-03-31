import numpy as np
from typing import Optional, List
from ros_games.src_pkg.core.base_game_engine import BaseGameEngine
from ros_games.src_pkg.controllers.vehicle_controller import GameState
from ros_games.src_pkg.entities.shape import Shape
from ros_games.src_pkg.config import Config
import random


class Game3ShapeRecognition(BaseGameEngine):
    """Game 3: Shape Recognition

    Colored shapes spawn randomly and remain visible for a limited duration.
    The vehicle must navigate to identify shapes via CV/visual processing.
    Points are awarded based on shape-color combinations.

    State Information for Controller:
        - vehicle_position, velocity, orientation (standard)
        - screen_frame: Current rendered frame as numpy array (H, W, 3)
        - active_shapes: List of currently visible Shape objects
        - current_score: Current score

    The controller can process the screen frame to identify shapes and navigate accordingly.
    """

    def __init__(self, config: Optional[Config] = None, headless: Optional[bool] = None):
        super().__init__(config, headless)

        # Game 3 specific config
        self.shape_types = self.config.game3_config['shapes']
        self.colors_config = self.config.game3_config['colors']
        self.shape_duration = self.config.game3_config['shape_duration']
        self.max_shapes = self.config.game3_config['max_shapes']
        self.spawn_interval = self.config.game3_config['spawn_interval']
        self.hard_mode = self.config.game3_config.get('hard_mode', False)
        self.shape_scoring = self.config.game3_config['shape_scoring']
        self.color_multipliers = self.config.game3_config['color_multipliers']
        self.episode_duration = self.config.game3_config['episode_duration']

        # Override max_time with episode duration
        self.max_time = self.episode_duration

        # Game state
        self.active_shapes: List[Shape] = []
        self.score = 0
        self.next_spawn_time = 0.0
        self.shape_counter = 0

        # Shape size
        self.shape_size = 40

    def get_game_mode(self) -> str:
        return "shape_recognition"

    def reset_game(self):
        """Reset game-specific state."""
        self.active_shapes = []
        self.score = 0
        self.next_spawn_time = self.spawn_interval
        self.shape_counter = 0

    def _spawn_shape(self):
        """Spawn a new random shape."""
        if len(self.active_shapes) >= self.max_shapes:
            return

        screen_width, screen_height = self.config.screen_dimensions
        margin = 100

        # Random position
        position = np.array([
            np.random.uniform(margin, screen_width - margin),
            np.random.uniform(margin, screen_height - margin)
        ])

        # Random shape type and color
        shape_type = random.choice(self.shape_types)
        color_name = random.choice(list(self.colors_config.keys()))
        color_rgb = tuple(self.colors_config[color_name])

        # Create shape
        shape_id = f"shape_{self.shape_counter:03d}"
        self.shape_counter += 1

        shape = Shape(
            shape_type=shape_type,
            color_name=color_name,
            color_rgb=color_rgb,
            position=position,
            size=self.shape_size,
            spawn_time=self.current_time,
            duration=self.shape_duration,
            shape_id=shape_id
        )

        self.active_shapes.append(shape)

        # Log spawn event
        if self.logger:
            self.logger.log_event(
                self.current_step,
                self.current_time,
                "shape_spawned",
                shape.to_dict()
            )

    def _remove_expired_shapes(self):
        """Remove shapes that have expired."""
        expired_shapes = [s for s in self.active_shapes if s.is_expired(self.current_time)]

        for shape in expired_shapes:
            self.active_shapes.remove(shape)

            # Log expiration
            if self.logger:
                self.logger.log_event(
                    self.current_step,
                    self.current_time,
                    "shape_expired",
                    {"shape_id": shape.shape_id}
                )

    def get_game_state(self) -> GameState:
        """Build GameState with shapes and frame."""
        state = super().get_game_state()

        # Add shape information
        state.active_shapes = self.active_shapes.copy()
        state.current_score = self.score

        # Add screen frame for CV processing
        state.screen_frame = self._capture_frame()

        return state

    def _capture_frame(self) -> Optional[np.ndarray]:
        """Capture current screen frame as numpy array.

        Returns:
            Frame as (H, W, 3) numpy array in RGB format, or None if headless
        """
        if self.headless or self.screen is None:
            return None

        import pygame

        # Get pixel array from pygame surface
        # pygame.surfarray.array3d returns (W, H, 3) in RGB
        frame = pygame.surfarray.array3d(self.screen)

        # Transpose to (H, W, 3)
        frame = np.transpose(frame, (1, 0, 2))

        return frame

    def update_game_logic(self):
        """Update shape spawning and expiration."""
        # Spawn new shapes if needed
        if self.current_time >= self.next_spawn_time:
            self._spawn_shape()
            self.next_spawn_time = self.current_time + self.spawn_interval

        # Remove expired shapes
        self._remove_expired_shapes()

    def add_score(self, shape_id: str, identified_as: str) -> bool:
        """Add score for correctly identifying a shape.

        This method should be called by the controller when it identifies a shape.

        Args:
            shape_id: ID of the shape being identified
            identified_as: String like "red_circle", "blue_square", etc.

        Returns:
            True if identification was correct and points awarded
        """
        # Find the shape
        shape = None
        for s in self.active_shapes:
            if s.shape_id == shape_id:
                shape = s
                break

        if shape is None:
            return False

        # Check if identification is correct
        correct_id = f"{shape.color_name}_{shape.shape_type}"
        is_correct = (identified_as == correct_id)

        if is_correct:
            # Calculate points based on shape type
            base_points = self.shape_scoring.get(shape.shape_type, 10)

            # Apply color multiplier if hard mode is enabled
            if self.hard_mode:
                multiplier = self.color_multipliers.get(shape.color_name, 1.0)
                points = int(base_points * multiplier)
            else:
                points = base_points

            self.score += points

            # Log score change
            if self.logger:
                self.logger.log_event(
                    self.current_step,
                    self.current_time,
                    "score_change",
                    {
                        "shape_id": shape_id,
                        "identified_as": identified_as,
                        "correct": True,
                        "points_awarded": points,
                        "base_points": base_points,
                        "hard_mode": self.hard_mode,
                        "new_score": self.score
                    }
                )

            return True
        else:
            # Log incorrect identification
            if self.logger:
                self.logger.log_event(
                    self.current_step,
                    self.current_time,
                    "incorrect_identification",
                    {
                        "shape_id": shape_id,
                        "identified_as": identified_as,
                        "correct_id": correct_id
                    }
                )

            return False

    def _get_telemetry_data(self):
        """Add score and shape count to telemetry."""
        data = super()._get_telemetry_data()

        data['score'] = self.score
        data['active_shapes'] = len(self.active_shapes)

        return data

    def render_game_elements(self):
        """Render shapes."""
        if self.headless:
            return

        import pygame

        # Render shapes
        for shape in self.active_shapes:
            # Get time remaining for fade effect
            time_remaining = shape.time_remaining(self.current_time)
            fade_threshold = 1.0  # Start fading in last second

            # Calculate alpha (transparency) for fading
            if time_remaining < fade_threshold:
                alpha_factor = max(0.3, time_remaining / fade_threshold)
            else:
                alpha_factor = 1.0

            # Adjust color brightness for fade
            color = tuple(int(c * alpha_factor) for c in shape.color_rgb)

            # Draw shape
            if shape.shape_type == "circle":
                pygame.draw.circle(
                    self.screen,
                    color,
                    shape.position.astype(int),
                    int(shape.size),
                    0  # Filled
                )
                # Border
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    shape.position.astype(int),
                    int(shape.size),
                    2
                )

            elif shape.shape_type == "square":
                half_size = shape.size / 2
                rect = pygame.Rect(
                    int(shape.position[0] - half_size),
                    int(shape.position[1] - half_size),
                    int(shape.size),
                    int(shape.size)
                )
                pygame.draw.rect(self.screen, color, rect, 0)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

            elif shape.shape_type == "triangle":
                # Equilateral triangle pointing up
                height = shape.size * 0.866  # sqrt(3)/2
                points = [
                    (shape.position[0], shape.position[1] - height * 0.67),  # Top
                    (shape.position[0] - shape.size / 2, shape.position[1] + height * 0.33),  # Bottom left
                    (shape.position[0] + shape.size / 2, shape.position[1] + height * 0.33),  # Bottom right
                ]
                pygame.draw.polygon(self.screen, color, points, 0)
                pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)

        # Display score
        font = pygame.font.Font(None, 36)
        score_text = f"Score: {self.score}"
        surface = font.render(score_text, True, (255, 255, 0))
        self.screen.blit(surface, (10, self.config.screen_dimensions[1] - 60))

        # Display active shapes count
        font_small = pygame.font.Font(None, 24)
        shapes_text = f"Active Shapes: {len(self.active_shapes)}"
        surface = font_small.render(shapes_text, True, (255, 255, 255))
        self.screen.blit(surface, (10, self.config.screen_dimensions[1] - 30))

    def check_game_termination(self) -> bool:
        """Terminate when episode duration reached."""
        return super().check_game_termination()

    def log_episode_start(self):
        """Log episode start."""
        if not self.logger:
            return

        self.logger.log_event(
            self.current_step,
            self.current_time,
            "episode_start",
            {
                "spawn_position": self.vehicle.position.tolist(),
                "spawn_orientation": float(self.vehicle.orientation),
                "episode_duration": self.episode_duration,
                "max_shapes": self.max_shapes,
                "shape_duration": self.shape_duration
            }
        )

    def log_episode_end(self):
        """Log episode end with score."""
        if not self.logger:
            return

        summary = {
            "total_steps": self.current_step,
            "total_time": self.current_time,
            "final_score": self.score,
            "shapes_spawned": self.shape_counter,
            "final_speed": self.vehicle.get_speed()
        }

        self.logger.log_event(
            self.current_step,
            self.current_time,
            "episode_end",
            {
                "reason": "time_limit",
                **summary
            }
        )

        self.logger.set_summary(summary)
