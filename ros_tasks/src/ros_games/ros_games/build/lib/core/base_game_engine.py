from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Dict, Any
from src.config import Config
from src.entities.vehicle import Vehicle
from src.core.logger import Logger
from src.controllers.vehicle_controller import VehicleController, GameState


class BaseGameEngine(ABC):
    """Base class for all training games.

    Provides:
    - Core game loop
    - Vehicle physics simulation
    - Controller integration
    - Logging (frame-level and event-level)
    - Headless mode support
    - Basic rendering (pygame)

    Subclasses must implement game-specific logic.
    """

    def __init__(self, config: Optional[Config] = None, headless: Optional[bool] = None):
        """Initialize game engine.

        Args:
            config: Configuration object (uses default if None)
            headless: Override headless mode from config
        """
        # Configuration
        self.config = config if config is not None else Config()

        # Headless mode
        self.headless = headless if headless is not None else self.config.headless

        # Initialize pygame (if not headless)
        if not self.headless:
            import pygame
            pygame.init()
            self.screen = pygame.display.set_mode(self.config.screen_dimensions)
            pygame.display.set_caption("AUV Training Arena")
            self.clock = pygame.time.Clock()
        else:
            self.screen = None
            self.clock = None

        # Game state
        self.running = False
        self.current_step = 0
        self.current_time = 0.0
        self.dt = 1.0 / self.config.target_fps

        # Vehicle
        self.vehicle = Vehicle(self.config, current_time=0.0)
        self._initialize_vehicle_position()

        # Controller (to be set by user)
        self.controller: Optional[VehicleController] = None

        # Logging
        self.logger: Optional[Logger] = None
        if self.config.logging['enabled']:
            episode_id = None if self.config.logging['auto_increment_episode'] else "000"
            self.logger = Logger(
                log_dir=self.config.logging['log_dir'],
                episode_id=episode_id
            )
            self.logger.set_game_mode(self.get_game_mode())
            self.logger.set_config(self._get_config_dict())

        # Episode termination conditions
        self.max_steps = self.config.max_steps
        self.max_time = self.config.max_time

    @abstractmethod
    def get_game_mode(self) -> str:
        """Return the game mode name for logging."""
        pass

    def _get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary for logging."""
        return self.config.config_dict

    def _initialize_vehicle_position(self):
        """Initialize vehicle position based on config."""
        screen_width, screen_height = self.config.screen_dimensions

        if self.config.submarine_parameters.get('spawn_random', False):
            # Random spawn (will be overridden by game-specific logic)
            margin = 50
            self.vehicle.position = np.array([
                np.random.uniform(margin, screen_width - margin),
                np.random.uniform(margin, screen_height - margin)
            ])
        elif self.config.submarine_parameters.get('spawn_position') is not None:
            # Fixed spawn position
            self.vehicle.position = np.array(
                self.config.submarine_parameters['spawn_position'],
                dtype=float
            )
        else:
            # Default: center of screen
            self.vehicle.position = np.array([screen_width / 2, screen_height / 2], dtype=float)

        # Random initial orientation
        self.vehicle.orientation = np.random.uniform(0, 2 * np.pi)

    def set_controller(self, controller: VehicleController):
        """Set the vehicle controller.

        Args:
            controller: VehicleController instance
        """
        self.controller = controller

    def get_game_state(self) -> GameState:
        """Build GameState object for controller.

        Subclasses should override to add game-specific state.
        """
        return GameState(
            vehicle_position=self.vehicle.position.copy(),
            vehicle_velocity=self.vehicle.velocity.copy(),
            vehicle_orientation=self.vehicle.orientation,
            vehicle_angular_velocity=self.vehicle.angular_velocity,
            current_time=self.current_time,
            current_step=self.current_step
        )

    def update(self):
        """Update game state for one step.

        1. Get controller input
        2. Apply forces to vehicle
        3. Update vehicle physics
        4. Update game-specific logic
        5. Log telemetry
        """
        # Get control from controller
        if self.controller is not None:
            state = self.get_game_state()
            force, torque = self.controller.compute_control(state)
            self.vehicle.apply_force(force)
            self.vehicle.apply_torque(torque)

        # Update vehicle physics
        self.vehicle.update(self.dt)

        # Constrain vehicle to screen bounds
        self._constrain_to_bounds()

        # Game-specific update
        self.update_game_logic()

        # Log telemetry
        if self.logger and self.config.logging['telemetry_enabled']:
            telemetry_data = self._get_telemetry_data()
            self.logger.log_telemetry(self.current_step, self.current_time, telemetry_data)

        # Update time
        self.current_time += self.dt
        self.current_step += 1

    @abstractmethod
    def update_game_logic(self):
        """Update game-specific logic.

        Called after vehicle physics update.
        Implement game-specific behavior here.
        """
        pass

    def _constrain_to_bounds(self):
        """Keep vehicle within screen bounds."""
        screen_width, screen_height = self.config.screen_dimensions
        self.vehicle.position[0] = np.clip(self.vehicle.position[0], 0, screen_width)
        self.vehicle.position[1] = np.clip(self.vehicle.position[1], 0, screen_height)

    def _get_telemetry_data(self) -> Dict[str, Any]:
        """Get telemetry data for logging.

        Subclasses can override to add game-specific telemetry.
        """
        return {
            'pos_x': self.vehicle.position[0],
            'pos_y': self.vehicle.position[1],
            'vel_x': self.vehicle.velocity[0],
            'vel_y': self.vehicle.velocity[1],
            'orientation': self.vehicle.orientation,
            'angular_velocity': self.vehicle.angular_velocity,
            'speed': self.vehicle.get_speed()
        }

    def render(self):
        """Render game to screen.

        Only called in visual mode.
        """
        if self.headless:
            return

        import pygame

        # Clear screen
        self.screen.fill(self.config.background_color)

        # Render game-specific elements
        self.render_game_elements()

        # Render vehicle
        self._render_vehicle()

        # Render telemetry overlay
        self._render_telemetry()

        # Update display
        pygame.display.flip()

    @abstractmethod
    def render_game_elements(self):
        """Render game-specific elements (targets, obstacles, etc.).

        Only called in visual mode.
        Implement game-specific rendering here.
        """
        pass

    def _render_vehicle(self):
        """Render the vehicle as a triangle."""
        if self.headless:
            return

        import pygame

        sub_width, sub_height = self.config.submarine_parameters['sub_size']

        # Triangle points (in vehicle local space)
        points = np.array([
            [sub_width / 2, 0],           # Nose
            [-sub_width / 2, sub_height / 2],   # Bottom left
            [-sub_width / 2, -sub_height / 2]   # Top left
        ])

        # Rotate points based on vehicle orientation
        cos_a = np.cos(self.vehicle.orientation)
        sin_a = np.sin(self.vehicle.orientation)
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        rotated_points = points @ rotation_matrix.T

        # Translate to world position
        world_points = rotated_points + self.vehicle.position

        # Draw vehicle
        pygame.draw.polygon(self.screen, (255, 255, 0), world_points, 0)
        pygame.draw.polygon(self.screen, (200, 200, 0), world_points, 2)

        # Draw nose indicator
        nose_pos = world_points[0].astype(int)
        pygame.draw.circle(self.screen, (255, 0, 0), nose_pos, 3)

    def _render_telemetry(self):
        """Render telemetry overlay."""
        if self.headless:
            return

        import pygame

        font = pygame.font.Font(None, 24)

        pos_text = f"Position: ({self.vehicle.position[0]:.1f}, {self.vehicle.position[1]:.1f})"
        vel_text = f"Velocity: ({self.vehicle.velocity[0]:.1f}, {self.vehicle.velocity[1]:.1f})"
        speed_text = f"Speed: {self.vehicle.get_speed():.1f}"
        angle_text = f"Angle: {np.degrees(self.vehicle.orientation):.1f} degrees"
        time_text = f"Time: {self.current_time:.2f}s | Step: {self.current_step}"

        y_offset = 10
        for text in [pos_text, vel_text, speed_text, angle_text, time_text]:
            surface = font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (10, y_offset))
            y_offset += 25

    def check_termination(self) -> bool:
        """Check if episode should terminate.

        Returns:
            True if episode should end
        """
        # Check step limit
        if self.max_steps is not None and self.current_step >= self.max_steps:
            if self.logger:
                self.logger.log_event(
                    self.current_step,
                    self.current_time,
                    "episode_end",
                    {"reason": "max_steps_reached"}
                )
            return True

        # Check time limit
        if self.max_time is not None and self.current_time >= self.max_time:
            if self.logger:
                self.logger.log_event(
                    self.current_step,
                    self.current_time,
                    "episode_end",
                    {"reason": "max_time_reached"}
                )
            return True

        # Game-specific termination
        return self.check_game_termination()

    @abstractmethod
    def check_game_termination(self) -> bool:
        """Check game-specific termination conditions.

        Returns:
            True if episode should end
        """
        pass

    def reset(self):
        """Reset episode.

        Called at start of each episode.
        """
        self.current_step = 0
        self.current_time = 0.0

        # Reset vehicle
        self.vehicle.velocity = np.array([0.0, 0.0])
        self.vehicle.angular_velocity = 0.0
        self.vehicle.acceleration = np.array([0.0, 0.0])
        self.vehicle.angular_acceleration = 0.0
        self.vehicle.current_time = 0.0
        self._initialize_vehicle_position()

        # Reset controller
        if self.controller:
            self.controller.reset()

        # Game-specific reset
        self.reset_game()

    @abstractmethod
    def reset_game(self):
        """Reset game-specific state.

        Called at start of each episode.
        """
        pass

    def run(self):
        """Run the game loop.

        Main entry point for running the game.
        """
        if self.controller is None:
            raise ValueError("Controller not set! Call set_controller() before run().")

        self.running = True
        self.reset()

        # Log episode start
        if self.logger:
            self.log_episode_start()

        # Main loop
        while self.running:
            # Handle events (pygame)
            if not self.headless:
                import pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False

            # Update
            self.update()

            # Render
            if not self.headless:
                self.render()
                self.clock.tick(self.config.target_fps)
            else:
                # In headless mode, show progress occasionally
                if self.current_step % 100 == 0:
                    print(f"Step {self.current_step}, Time: {self.current_time:.2f}s")

            # Check termination
            if self.check_termination():
                self.running = False

        # Cleanup
        self.log_episode_end()
        if self.logger:
            self.logger.close()

        if not self.headless:
            import pygame
            pygame.quit()

    @abstractmethod
    def log_episode_start(self):
        """Log episode start event.

        Subclasses should log game-specific initial state.
        """
        pass

    @abstractmethod
    def log_episode_end(self):
        """Log episode end event and summary.

        Subclasses should compute and log game-specific summary.
        """
        pass
