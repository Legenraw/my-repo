from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Any
import numpy as np


@dataclass
class GameState:
    vehicle_position: np.ndarray
    vehicle_velocity: np.ndarray
    vehicle_orientation: float
    vehicle_angular_velocity: float
    current_time: float
    current_step: int
    target_position: Optional[np.ndarray] = None
    distance_to_target: Optional[float] = None
    obstacles: List[Any] = field(default_factory=list)
    screen_frame: Optional[np.ndarray] = None
    active_shapes: List[Any] = field(default_factory=list)
    active_images: List[Any] = field(default_factory=list)
    current_score: int = 0


class VehicleController(ABC):
    
    def __init__(self, config):
        self.config = config
        self.max_thrust = config.submarine_parameters['sub_max_thrust']
        self.max_torque = config.submarine_parameters['sub_max_torque']
        self.dt = 0.016
    
    @abstractmethod
    def compute_control(self, state: GameState) -> Tuple[np.ndarray, float]:
        pass
    
    def reset(self):
        pass
    
    def _limit_force(self, force: np.ndarray) -> np.ndarray:
        force_mag = np.linalg.norm(force)
        if force_mag > self.max_thrust:
            return (force / force_mag) * self.max_thrust
        return force
    
    def _limit_torque(self, torque: float) -> float:
        return np.clip(torque, -self.max_torque, self.max_torque)
    
    def _normalize_angle(self, angle: float) -> float:
        return np.arctan2(np.sin(angle), np.cos(angle))

