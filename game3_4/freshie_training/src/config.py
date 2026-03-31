config_dict = {
  # General settings
  "game_mode": "target_reaching",  # or "obstacle_avoidance", "shape_recognition", "ml_recognition"
  "headless": False,
  "screen_dimensions": (1280, 720),
  "target_fps": 60,
  "background_color": (0, 119, 190),
  "max_steps": None,  # None = unlimited
  "max_time": None,   # None = unlimited

  # Logging configuration
  "logging": {
    "enabled": True,
    "log_dir": "./logs",
    "telemetry_enabled": True,
    "events_enabled": True,
    "auto_increment_episode": True
  },

  # Physics simulation
  "physics_constants": {
    "water_density": 1000,
    "gravity": 9.81,
    "drag_coefficient": 0.00001,
    "angular_drag_coefficient": 0.0001,
    "enable_currents": False,
    "current_strength": 50,
    "current_direction": [1.0, 0.0],
    "turbulence_enabled": False
  },

  # Vehicle parameters
  "submarine_parameters": {
    "mass": 100,
    "moment_of_inertia": 10,
    "drag_area": 0.5,
    "sub_max_thrust": 50000,  # Reduced from 200000 (divided by 10)
    "sub_max_torque": 5,      # Reduced from 50 (divided by 10)
    "max_velocity": 300,       # Linear velocity cap (px/s)
    "max_angular_velocity": 2.0,  # Angular velocity cap (rad/s)
    "sub_size": (30, 10),
    "spawn_random": False,
    "spawn_position": None  # None = center, or [x, y]
  },

  # Game 1: Target Reaching
  "game1_config": {
    "success_radius": 30,
    "target_spawn_margin": 50,
    "auto_reset": False,
    "stability_duration": 2.0  # Seconds vehicle must stay inside target radius
  },

  # Game 2: Obstacle Avoidance
  "game2_config": {
    "num_obstacles": 5,
    "obstacle_radius_range": [20, 50],
    "min_spacing": 100,
    "collision_ends_episode": False,
    "collision_penalty": 10
  },

  # Game 3: Shape Recognition
  "game3_config": {
    "shapes": ["circle", "square", "triangle"],
    "colors": {
      "red": [255, 0, 0],
      "blue": [0, 0, 255],
      "green": [0, 255, 0]
    },
    "shape_duration": 5.0,
    "max_shapes": 3,
    "spawn_interval": 2.0,
    "hard_mode": False,  # Toggle for color-based scoring multipliers
    "shape_scoring": {
      "circle": 10,
      "square": 15,
      "triangle": 20
    },
    "color_multipliers": {
      "red": 0.5,
      "blue": 1.0,
      "green": 1.5
    },
    "episode_duration": 60.0
  },

  # Game 4: ML Recognition
  "game4_config": {
    "dataset": "mnist",
    "dataset_path": "./datasets/mnist",
    "image_display_size": [64, 64],
    "image_duration": 4.5,  # Doubled from 3.0
    "max_images": 6,
    "spawn_interval": 0.4,
    "points_per_correct": 20,  # Legacy: now uses digit value + 1
    "episode_duration": 60.0
  }
}


class Config:
  def __init__(self):
    object.__setattr__(self, 'config_dict', config_dict)

  def __getattr__(self, name):
    return self.config_dict[name]

  def __setattr__(self, name, value):
    if name == 'config_dict':
      object.__setattr__(self, name, value)
    else:
      self.config_dict[name] = value
  
  def __delattr__(self, name):
    del self.config_dict[name]
  
  def __contains__(self, name):
    return name in self.config_dict
  
  def __iter__(self):
    return iter(self.config_dict)


if __name__ == "__main__":
  config = Config()
  print(config.screen_dimensions)
  print(config.target_fps)
  print(config.background_color)
  print(config.physics_constants)
  print(config.submarine_parameters)