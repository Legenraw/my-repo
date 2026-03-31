import pid as p
prop=p.P_controller()
inte=p.I_controller()
diff=p.D_controller()
pid=p.PID_controller()
setpoint=float(input("Enter setpoint:"))
def f(y):
    return 2*y
x=float(input("Enter initial input:"))
while(abs(f(x)-setpoint)>0.01):
    error=setpoint-f(x)
    change=pid.total_action(prop,inte,diff,error,1)
    x+=change
    print(x)

    
