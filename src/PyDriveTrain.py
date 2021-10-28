#!/usr/bin/env python
from  PID import PID

class Drive:
    left_pid=PID(0,0,0)
    right_pid = PID(0, 0, 0)


    def __init__(self,p,i,d,min_out=-1,max_out=1,deadband=0.1):
        self.deadband=deadband
        self.left_pid=PID(p,i,d,output_abs_limit={"max": max_out, "min": min_out},windup_max=3000)

        self.right_pid=PID(p,i,d,output_abs_limit={"max": max_out, "min": min_out},windup_max=3000)


    def update(self,linear,angular,left_live,right_live):
        left_set,right_set=self.control2wheels(linear,angular)
        # print left_set,right_set
        self.left_pid.SetPoint=left_set
        self.right_pid.SetPoint=right_set

        left_ret=self.left_pid(left_live)
        right_ret=self.right_pid(right_live)
        left_ret=left_ret if abs(left_ret)>self.deadband else 0
        right_ret = right_ret if abs(right_ret) > self.deadband else 0
        return left_ret,right_ret
        pass

    @staticmethod
    def wheels2control(left, right):

        linear=(left+right)/2
        angular=(left-right)/2
        return linear, angular

    @staticmethod
    def control2wheels(linear, angular):

        left=linear-angular
        right=linear+angular
        if abs(max(left,right,key=abs))>2500:
            larger_val=abs(max(left, right, key=abs))
            left=left/larger_val
            right=right/larger_val

        return left,right
    def clear(self):
        self.left_pid.clear()
        self.right_pid.clear()
    pass