import math
class Throw:
    def __init__(self,peak_val,fly_line,time,tof):
        self.time = time
        self.peak_val = round(peak_val,2)
        self.fly_line = fly_line
        self.tof = round(tof/1000,2)
        self.THROW_ON_FLOOR = False
        self.air_rolls = 0
        self.angle = 0
        self.distance = 0

    def set_angle(self, angle):
        self.angle = round(math.degrees(angle),1)

    def is_on_floor(self):
        self.THROW_ON_FLOOR = True

    def set_air_rolls(self,rolls):
        self.air_rolls = rolls

    def set_distance(self, distance):
        self.distance = round(distance,2)

    def print(self):
        print(f"THROW AT {self.time}")


class Roll:
    def __init__(self, time, last, next):
        self.time = time
        self.last = last
        self.next = next
    def print(self):
        print(f"ROLL HAPPENED AT {self.time} FROM SIDE {self.last}  TO SIDE {self.next}")