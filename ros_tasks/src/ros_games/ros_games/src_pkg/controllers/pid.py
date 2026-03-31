class P_controller:
    def __init__(self,K):
        self.Kp=K
    def P_action(self,error):
        return self.Kp*error
class I_controller:
    def __init__(self,K):
        self.Ki=K
        self.totalError=0
    def I_action(self,error,timestep):
        self.totalError+=error;
        return self.Ki*self.totalError*timestep
class D_controller:
    def __init__(self,K):
        self.Kd=K
        self.prev_error=0
    def D_action(self,error,t):
        if(self.prev_error==0):
            self.prev_error=error
            return 0
        error_dif=error-self.prev_error
        self.prev_error=error
        return self.Kd*error_dif/t
class PID_controller:
    def __init__(self,kp,ki,kd):
        self.p=P_controller(kp)
        self.i=I_controller(ki)
        self.d=D_controller(kd)
    def total_action(self,error,timestep):
        return self.p.P_action(error)+self.i.I_action(error,timestep)+self.d.D_action(error,timestep)



