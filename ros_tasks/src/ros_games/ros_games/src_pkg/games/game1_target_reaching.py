import numpy as np
from typing import Optional
from ros_games.src_pkg.core.base_game_engine import BaseGameEngine
from ros_games.src_pkg.controllers.vehicle_controller import GameState
from ros_games.src_pkg.entities.target import Target
from ros_games.src_pkg.config import Config


class Game1TargetReaching(BaseGameEngine):
    """Game 1: Target Reaching

    The vehicle spawns at a random position and must navigate to a target position.
    Success occurs when the vehicle reaches within the success radius of the target.

    State Information for Controller:
        - vehicle_position: Current position [x, y]
        - vehicle_velocity: Current velocity [vx, vy]
        - vehicle_orientation: Current orientation (radians)
        - target_position: Target position [x, y]
        - distance_to_target: Distance to target
    """

    def __init__(self, config: Optional[Config] = None, headless: Optional[bool] = None):
        super().__init__(config, headless)

        # Game-specific config
        self.success_radius = self.config.game1_config['success_radius']
        self.target_spawn_margin = self.config.game1_config['target_spawn_margin']
        self.auto_reset = self.config.game1_config['auto_reset']
        self.stability_duration = self.config.game1_config.get('stability_duration', 2.0)

        # Target
        self.target: Optional[Target] = None

        # Episode tracking
        self.episode_success = False
        self.time_inside_target = 0.0  # Track time spent inside target radius

    def get_game_mode(self) -> str:
        return "target_reaching"

    def reset_game(self):
        """Reset game-specific state."""
        # Generate random target position
        screen_width, screen_height = self.config.screen_dimensions
        margin = self.target_spawn_margin

        target_pos = np.array([
            np.random.uniform(margin, screen_width - margin),
            np.random.uniform(margin, screen_height - margin)
        ])

        self.target = Target(target_pos, self.success_radius)
        self.episode_success = False
        self.time_inside_target = 0.0

    def get_game_state(self) -> GameState:
        """Build GameState with target information."""
        state = super().get_game_state()

        # Add target information
        if self.target:
            state.target_position = self.target.position.copy()
            state.distance_to_target = self.target.distance_to(self.vehicle.position)

        return state

    def update_game_logic(self):
        """Check if target is reached with stability requirement."""
        if self.target and self.target.is_reached(self.vehicle.position):
            # Vehicle is inside target radius - accumulate time
            self.time_inside_target += self.dt

            # Check if stability duration requirement is met
            if self.time_inside_target >= self.stability_duration and not self.episode_success:
                self.episode_success = True

                if self.logger:
                    self.logger.log_event(
                        self.current_step,
                        self.current_time,
                        "target_reached",
                        {
                            "final_position": self.vehicle.position.tolist(),
                            "final_distance": self.target.distance_to(self.vehicle.position),
                            "time_to_reach": self.current_time,
                            "steps_to_reach": self.current_step,
                            "stability_time": self.time_inside_target
                        }
                    )
        else:
            # Vehicle left target radius - reset stability timer
            self.time_inside_target = 0.0

    def _get_telemetry_data(self):
        """Add target distance to telemetry."""
        data = super()._get_telemetry_data()

        if self.target:
            data['distance_to_target'] = self.target.distance_to(self.vehicle.position)

        return data

    def render_game_elements(self):
        """Render target."""
        if self.headless or not self.target:
            return

        import pygame

        # Draw target as circle
        target_color = (0, 255, 0) if self.episode_success else (255, 100, 100)
        pygame.draw.circle(
            self.screen,
            target_color,
            self.target.position.astype(int),
            int(self.target.radius),
            0  # Filled circle
        )

        # Draw border
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            self.target.position.astype(int),
            int(self.target.radius),
            2  # Border only
        )

        # Draw line from vehicle to target
        pygame.draw.line(
            self.screen,
            (150, 150, 150),
            self.vehicle.position.astype(int),
            self.target.position.astype(int),
            1
        )

        # Display distance
        font = pygame.font.Font(None, 24)
        distance = self.target.distance_to(self.vehicle.position)
        dist_text = f"Distance: {distance:.1f}"
        surface = font.render(dist_text, True, (255, 255, 255))
        self.screen.blit(surface, (10, self.config.screen_dimensions[1] - 30))

    def check_game_termination(self) -> bool:
        """Terminate if target reached (and auto_reset is False)."""
        if self.episode_success and not self.auto_reset:
            return True
        return False

    def log_episode_start(self):
        """Log episode start with target position."""
        if not self.logger:
            return

        self.logger.log_event(
            self.current_step,
            self.current_time,
            "episode_start",
            {
                "spawn_position": self.vehicle.position.tolist(),
                "spawn_orientation": float(self.vehicle.orientation),
                "target_position": self.target.position.tolist() if self.target else None,
                "success_radius": self.success_radius
            }
        )

    def log_episode_end(self):
        """Log episode end and summary."""
        if not self.logger:
            return

        # Calculate summary statistics
        final_distance = self.target.distance_to(self.vehicle.position) if self.target else None
        avg_speed = np.mean([
            # We don't have historical speeds, so just use final speed
            self.vehicle.get_speed()
        ])

        summary = {
            "total_steps": self.current_step,
            "total_time": self.current_time,
            "success": self.episode_success,
            "final_distance": final_distance,
            "final_speed": self.vehicle.get_speed(),
        }

        self.logger.log_event(
            self.current_step,
            self.current_time,
            "episode_end",
            {
                "reason": "target_reached" if self.episode_success else "terminated",
                **summary
            }
        )

        self.logger.set_summary(summary)
