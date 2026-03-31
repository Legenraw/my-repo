import numpy as np
import random
from typing import Tuple
from ros_games.src_pkg.controllers.vehicle_controller import VehicleController, GameState
from ros_games.src_pkg.controllers import pid
import sys
import rclpy
from rclpy.node import Node
from ros_msg.srv import Reset

class reset_client(Node):
    def __init__(self):
        super().__init__('reset_client')
        self.cli = self.create_client(Reset, 'num_of_obstacles')
        self.req=Reset.Request()
        
    def send_request(self,num):
        self.req.obstacle_num=num
        return self.cli.call_async(self.req)


class PIDControllerGame1(VehicleController):
    rclpy.init()
    print(pid.__file__)
    def __init__(self, config):
        super().__init__(config)
        self.fmag=0
        self.fpid=pid.PID_controller(20,2,10)
        self.amag=0
        self.apid=pid.PID_controller(10000,0,250)
        pass

    def compute_control(self, state: GameState) -> Tuple[np.ndarray, float]:
        # Computing Force
        delx=state.target_position[0]-state.vehicle_position[0]
        dely=state.target_position[1]-(state.vehicle_position[1])
        aSet=np.arctan2(dely,delx)
        direction=np.array([np.cos(aSet),-1*np.sin(-1*aSet)])
        error=state.distance_to_target
        change=self.fpid.total_action(error,0.016)
        self.fmag+=change
        # Computing Force
        
        # Obstacle avoid
        extra_force=np.array([0.0,0.0])
        for item in state.obstacles:
            k=7000000000
            minD=200
            dx=state.vehicle_position[0]-item.position[0]
            dy=state.vehicle_position[1]-item.position[1]
            r=np.sqrt(dx*dx + dy*dy)
            if(r<minD):
                extra_force[0]+=((k*dx)/r)*((1/r)-(1/minD))*((1/r)-(1/minD))
                extra_force[1]+=((k*dy)/r)*((1/r)-(1/minD))*((1/r)-(1/minD))
            else:
                extra_force[0]+=0
                extra_force[1]+=0
        print(state.distance_to_target)
        # Obstacle avoid

        # Computing Torque
        aError= aSet - state.vehicle_orientation
        errorMag=0
        if(aError<-1*np.pi or (aError>0 and aError<np.pi)):
            errorMag=aError%(2*np.pi)
        else:
            errorMag=-1*((2*np.pi-aError)%(2*np.pi))
        achange=self.apid.total_action(errorMag,0.016)
        self.amag=achange
        # Computing Torque
        if(state.distance_to_target<1):
            resetter=reset_client()
            num=random.randint(1,15)
            future = resetter.send_request(num)
            response = future.result()
            #print(response.obstacle_number)
            resetter.destroy_node()

        return self.fmag*direction+extra_force, self.amag

    def reset(self):
        self.last_pos_error = np.array([0.0, 0.0])
        self.last_orientation_error = 0.0

