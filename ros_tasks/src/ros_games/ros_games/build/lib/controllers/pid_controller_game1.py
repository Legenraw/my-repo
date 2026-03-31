import numpy as np
from typing import Tuple
from src.controllers.vehicle_controller import VehicleController, GameState


class PIDControllerGame1(VehicleController):

    def __init__(self, config,
                 pos_kp: float,
                 pos_kd: float,
                 rot_kp: float,
                 rot_kd: float):
        super().__init__(config)
        pass

    def compute_control(self, state: GameState) -> Tuple[np.ndarray, float]:
        return np.array([0.0, 0.0]), 0.0
        #return force, torque

    def reset(self):
        self.last_pos_error = np.array([0.0, 0.0])
        self.last_orientation_error = 0.0

