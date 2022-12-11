class Throw:
    def __init__(self,peak_val,fly_line,time):
        self.time=time
        self.peak_val=round(peak_val,2)
        self.fly_line=fly_line
        self.tof = len(fly_line)
        self.THROW_ON_FLOOR = False
        self.air_rolls=0
    def is_on_floor(self):
        self.THROW_ON_FLOOR = True
    def set_air_rolls(self,rolls):
        self.air_rolls=rolls
    def print(self):
        print(f"THROW AT {self.time}")
class Roll:
    def __init__(self,time,last,next):
        self.time = time
        self.last = last
        self.next = next
    def print(self):
        print(f"ROLL HAPPENED AT {self.time} FROM SIDE {self.last}  TO SIDE {self.next}")