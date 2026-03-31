import numpy as np
from typing import Optional, List
from ros_games.src_pkg.games.game1_target_reaching import Game1TargetReaching
from ros_games.src_pkg.controllers.vehicle_controller import GameState
from ros_games.src_pkg.entities.obstacle import Obstacle
from ros_games.src_pkg.config import Config


class Game2ObstacleAvoidance(Game1TargetReaching):
    """Game 2: Obstacle Avoidance

    Extension of Game 1 with obstacles placed randomly in the environment.
    The vehicle must navigate to the target while avoiding collisions.

    State Information for Controller:
        - All Game 1 state (position, velocity, target, etc.)
        - obstacles: List of Obstacle objects
        - collision_detected: Boolean indicating if currently colliding
        - nearest_obstacle_distance: Distance to nearest obstacle surface
    """

    def __init__(self, config: Optional[Config] = None, headless: Optional[bool] = None):
        super().__init__(config, headless)

        # Game 2 specific config
        self.num_obstacles = self.config.game2_config['num_obstacles']
        self.obstacle_radius_range = self.config.game2_config['obstacle_radius_range']
        self.min_spacing = self.config.game2_config['min_spacing']
        self.collision_ends_episode = self.config.game2_config['collision_ends_episode']
        self.collision_penalty = self.config.game2_config['collision_penalty']

        # Obstacles
        self.obstacles: List[Obstacle] = []

        # Collision tracking
        self.collision_detected = False
        self.collision_count = 0
        self.total_penalty = 0

        # Vehicle radius for collision detection (approximation)
        sub_width = self.config.submarine_parameters['sub_size'][0]
        self.vehicle_radius = sub_width / 2

    def get_game_mode(self) -> str:
        return "obstacle_avoidance"

    def reset_game(self):
        """Reset game-specific state including obstacles."""
        # Reset parent (target generation)
        super().reset_game()

        # Generate obstacles
        self.obstacles = self._generate_obstacles()

        # Reset collision tracking
        self.collision_detected = False
        self.collision_count = 0
        self.total_penalty = 0

    def _generate_obstacles(self) -> List[Obstacle]:
        """Generate obstacles with spacing constraints.

        Ensures:
        - Obstacles ARE placed in the path between spawn and target
        - Obstacles don't overlap with spawn position
        - Obstacles don't overlap with target
        - Obstacles maintain minimum spacing from each other
        - Mix of path obstacles and random obstacles for challenge
        """
        screen_width, screen_height = self.config.screen_dimensions
        obstacles = []

        num_path_obstacles = max(3, self.num_obstacles // 2)
        num_random_obstacles = self.num_obstacles - num_path_obstacles

        spawn_pos = self.vehicle.position
        target_pos = self.target.position if self.target else np.array([screen_width/2, screen_height/2])
        
        path_vector = target_pos - spawn_pos
        path_length = np.linalg.norm(path_vector)
        path_direction = path_vector / path_length
        perpendicular = np.array([-path_direction[1], path_direction[0]])

        for i in range(num_path_obstacles):
            max_attempts = 100
            for attempt in range(max_attempts):
                t = (i + 1) / (num_path_obstacles + 1)
                point_on_path = spawn_pos + t * path_vector
                
                offset_distance = np.random.uniform(-80, 80)
                noise = np.random.uniform(-30, 30)
                
                pos = point_on_path + offset_distance * perpendicular + noise * path_direction
                
                pos[0] = np.clip(pos[0], 50, screen_width - 50)
                pos[1] = np.clip(pos[1], 50, screen_height - 50)
                
                radius = np.random.uniform(
                    self.obstacle_radius_range[0],
                    self.obstacle_radius_range[1]
                )
                
                if np.linalg.norm(pos - spawn_pos) < self.min_spacing + radius:
                    continue
                
                if np.linalg.norm(pos - target_pos) < self.min_spacing + radius:
                    continue
                
                too_close = False
                for obs in obstacles:
                    distance = np.linalg.norm(pos - obs.position)
                    if distance < self.min_spacing + radius + obs.radius:
                        too_close = True
                        break
                
                if not too_close:
                    obstacles.append(Obstacle(pos, radius, obstacle_id=len(obstacles)))
                    break

        max_attempts = 1000
        attempts = 0
        while len(obstacles) < self.num_obstacles and attempts < max_attempts:
            attempts += 1
            
            pos = np.array([
                np.random.uniform(50, screen_width - 50),
                np.random.uniform(50, screen_height - 50)
            ])
            
            radius = np.random.uniform(
                self.obstacle_radius_range[0],
                self.obstacle_radius_range[1]
            )
            
            if np.linalg.norm(pos - spawn_pos) < self.min_spacing + radius:
                continue
            
            if np.linalg.norm(pos - target_pos) < self.min_spacing + radius:
                continue
            
            too_close = False
            for obs in obstacles:
                distance = np.linalg.norm(pos - obs.position)
                if distance < self.min_spacing + radius + obs.radius:
                    too_close = True
                    break
            
            if too_close:
                continue
            
            obstacles.append(Obstacle(pos, radius, obstacle_id=len(obstacles)))

        if len(obstacles) < self.num_obstacles:
            print(f"Warning: Only generated {len(obstacles)} obstacles out of {self.num_obstacles} requested")

        return obstacles

    def get_game_state(self) -> GameState:
        """Build GameState with obstacle information."""
        state = super().get_game_state()

        # Add obstacle information
        state.obstacles = self.obstacles.copy()

        return state

    def update_game_logic(self):
        """Check for target reached and collisions."""
        # Check target (parent class logic)
        super().update_game_logic()

        # Check collisions
        previous_collision = self.collision_detected
        self.collision_detected = False

        for obstacle in self.obstacles:
            if obstacle.check_collision(self.vehicle.position, self.vehicle_radius):
                self.collision_detected = True

                # Log collision event (only on first detection)
                if not previous_collision and self.logger:
                    self.collision_count += 1
                    self.total_penalty += self.collision_penalty

                    self.logger.log_event(
                        self.current_step,
                        self.current_time,
                        "collision",
                        {
                            "obstacle_id": obstacle.id,
                            "obstacle_position": obstacle.position.tolist(),
                            "vehicle_position": self.vehicle.position.tolist(),
                            "collision_number": self.collision_count,
                            "penalty": self.collision_penalty,
                            "total_penalty": self.total_penalty
                        }
                    )

                break  # Only need to detect one collision

    def _get_nearest_obstacle_distance(self) -> float:
        """Get distance to nearest obstacle surface."""
        if not self.obstacles:
            return float('inf')

        min_distance = float('inf')
        for obstacle in self.obstacles:
            distance = obstacle.distance_to(self.vehicle.position)
            min_distance = min(min_distance, distance)

        return min_distance

    def _get_telemetry_data(self):
        """Add collision and obstacle data to telemetry."""
        data = super()._get_telemetry_data()

        data['colliding'] = self.collision_detected
        data['nearest_obstacle'] = self._get_nearest_obstacle_distance()

        return data

    def render_game_elements(self):
        """Render target and obstacles."""
        # Render target (parent class)
        super().render_game_elements()

        if self.headless:
            return

        import pygame

        # Render obstacles
        for obstacle in self.obstacles:
            # Check if vehicle is colliding with this obstacle
            is_colliding = obstacle.check_collision(self.vehicle.position, self.vehicle_radius)

            # Color: red if colliding, gray otherwise
            color = (255, 100, 100) if is_colliding else (100, 100, 100)

            # Draw filled circle
            pygame.draw.circle(
                self.screen,
                color,
                obstacle.position.astype(int),
                int(obstacle.radius),
                0  # Filled
            )

            # Draw border
            border_color = (255, 0, 0) if is_colliding else (150, 150, 150)
            pygame.draw.circle(
                self.screen,
                border_color,
                obstacle.position.astype(int),
                int(obstacle.radius),
                2  # Border
            )

        # Display collision count
        if self.collision_count > 0:
            font = pygame.font.Font(None, 24)
            collision_text = f"Collisions: {self.collision_count} | Penalty: {self.total_penalty}"
            surface = font.render(collision_text, True, (255, 100, 100))
            self.screen.blit(surface, (10, self.config.screen_dimensions[1] - 60))

    def check_game_termination(self) -> bool:
        """Terminate if target reached or collision (if configured)."""
        # Check parent termination (target reached, time/step limits)
        #if super().check_game_termination():
        #    return True

        # Check collision termination
        if self.collision_ends_episode and self.collision_detected:
            if self.logger:
                self.logger.log_event(
                    self.current_step,
                    self.current_time,
                    "episode_end",
                    {"reason": "collision"}
                )
            return True

        return False

    def log_episode_start(self):
        """Log episode start with obstacles."""
        # Log parent (target info)
        super().log_episode_start()

        # Log obstacles
        if self.logger:
            self.logger.log_event(
                self.current_step,
                self.current_time,
                "obstacles_generated",
                {
                    "num_obstacles": len(self.obstacles),
                    "obstacles": [obs.to_dict() for obs in self.obstacles]
                }
            )

    def log_episode_end(self):
        """Log episode end with collision statistics."""
        if not self.logger:
            return

        # Calculate summary statistics
        final_distance = self.target.distance_to(self.vehicle.position) if self.target else None

        summary = {
            "total_steps": self.current_step,
            "total_time": self.current_time,
            "success": self.episode_success,
            "final_distance": final_distance,
            "final_speed": self.vehicle.get_speed(),
            "collision_count": self.collision_count,
            "total_penalty": self.total_penalty,
            "num_obstacles": len(self.obstacles)
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
