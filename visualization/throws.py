class Throw:
    def __init__(self,peak_val,fly_line,time):
        self.time=time
        self.peak_val=round(peak_val,2)
        self.fly_line=fly_line
        self.tof = len(fly_line)
        self.THROW_ON_FLOOR = False
    def is_on_floor(self):
        self.THROW_ON_FLOOR = True