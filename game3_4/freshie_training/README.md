# PID Control Training Games

Learn PID control through interactive vehicle navigation challenges.

## Controller Interface

Your controller receives a `GameState` object each frame:

```python
state.vehicle_position      # np.array [x, y]
state.vehicle_velocity      # np.array [vx, vy]
state.vehicle_orientation   # float (radians)
state.vehicle_angular_velocity  # float (rad/s)
state.current_time          # float (seconds)
```

Return `(force, torque)` - force as `np.array([fx, fy])`, torque as float.

---

## Games

### Game 1: Target Reaching
Navigate to target and **hold position for 2 seconds**.

**State:** `state.target_position`, `state.distance_to_target`

**Config:**
| Option | Default | Description |
|--------|---------|-------------|
| `success_radius` | 30 | Distance threshold (px) |
| `stability_duration` | 2.0 | Hold time required (s) |

---

### Game 2: Obstacle Avoidance
Reach target while avoiding obstacles.

**State:** `state.target_position`, `state.obstacles` (list of Obstacle objects with `.position`, `.radius`)

**Config:**
| Option | Default | Description |
|--------|---------|-------------|
| `num_obstacles` | 5 | Obstacle count |
| `collision_penalty` | 10 | Points lost per hit |

---

### Game 3: Shape Recognition
Identify colored shapes before they expire.

**Available data:**
- `state.screen_frame` - RGB frame (H, W, 3) for CV processing
- `state.active_shapes` - list with shape metadata

**Shape properties:**
```python
shape.position      # np.array [x, y] - center position
shape.size          # float - radius/side length in pixels
shape.color_rgb     # tuple (R, G, B) - for color detection
```

Use `screen_frame` for computer vision to detect shape type and color at each position.

**Scoring:** Circle 10 | Square 15 | Triangle 20 pts
**Hard mode:** Multiply by color (red 0.5x, blue 1x, green 1.5x)

**Config:**
| Option | Default | Description |
|--------|---------|-------------|
| `hard_mode` | false | Enable color multipliers |
| `shape_duration` | 5.0 | Time before expiry (s) |
| `max_shapes` | 3 | Max simultaneous |

---

### Game 4: ML Recognition
Identify MNIST digits before they expire.

**Available data:**
- `state.screen_frame` - RGB frame (H, W, 3) for visual processing
- `state.active_images` - list with image metadata

**Image properties:**
```python
image.image         # np.array (28, 28) - grayscale digit for ML classification
image.position      # np.array [x, y] - center position on screen
image.display_size  # tuple (w, h) - rendered size (64x64)
```

Use `image.image` (28x28 grayscale) as input to your digit classifier.

**Scoring:** Points = digit + 1 (0→1pt, 9→10pts)

**Config:**
| Option | Default | Description |
|--------|---------|-------------|
| `image_duration` | 6.0 | Time before expiry (s) |
| `max_images` | 2 | Max simultaneous |

---

## Vehicle Config

| Option | Default | Description |
|--------|---------|-------------|
| `sub_max_thrust` | 50000 | Max force |
| `sub_max_torque` | 5 | Max rotation torque |
| `max_velocity` | 100 | Speed cap (px/s) |
| `max_angular_velocity` | 2.0 | Rotation cap (rad/s) |

Edit in `src/config.py`.
