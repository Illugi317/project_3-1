import pandas as pd
import sys
import pandas as pd
import sys, math
from os.path import dirname, abspath, join
from scipy.signal import find_peaks
from os import makedirs
import matplotlib.pyplot as plt
import numpy as np
import statistics
from throws import Throw
from math import sqrt
from numpy import arccos
DIR_ROOT = dirname(dirname(abspath(__file__)))
DIR_VISUAL = join(DIR_ROOT,"visualization")
DIR_IMG = join(DIR_VISUAL,"images")
DIR_CSV = join(DIR_ROOT, "csv")
file_path = join(DIR_CSV, "throw_overhead.csv")

for d in [DIR_VISUAL, DIR_IMG, DIR_CSV, ]:
    makedirs(d, exist_ok=True)


def read_csv(csv_name):
    try:
        data = pd.read_csv(csv_name, sep=",", encoding='utf-8')
        return data
    except Exception:
        print("Something went wrong when trying to open the csv file!")
        sys.exit(2)
def solve(path):
    acc_sum =[]
    lin_sum = []
    times = []
    df = read_csv(path)
    orix = df.orix
    oriy = df.oriy
    oriz = df.oriz

    gravx = df.gravx
    gravy = df.gravy
    gravz = df.gravz
    linx = df.linerx
    liny = df.linery
    linz = df.linerz
    accx = df.accx
    accy = df.accy
    accz = df.accz
    first_vals =  [0.59,9.15,-3.47]
    square_root = (sqrt(pow(first_vals[0],2)+pow(first_vals[1],2)+pow(first_vals[2],2)))
    A_matrix = [i/square_root for i in first_vals]
    G_matrix = [0,0,-1]
    cosinus = -1*A_matrix[2]
    theta =arccos(cosinus)
    Ax = A_matrix[0]
    Ay = A_matrix[1]
    Az = A_matrix[2]
    common_bottom = pow(Ax,2) + pow(Ay,2)
    first_top = (pow(Ay,2) - (pow(Ax, 2)*Az))
    third_top = (pow(Ax,2) - (pow(Ay,2)*Az))
    second_top = (-1*Ax*Ay - Ax*Ay*Az)
    t1 = first_top/common_bottom
    t2 = second_top/common_bottom
    t3 = Ax
    m1 = second_top/common_bottom
    m2 = third_top/common_bottom
    m3 = Ay
    b1 = -1*Ax
    b2 = -1*Ay
    b3 = -1*Az
    top = [t1,t2,t3]
    mid = [m1,m2,m3]
    bot = [b1,b2,b3]
    rotation_matrix = [top,mid,bot]
    hopefully_good = np.dot(rotation_matrix,first_vals)
    rotation = [orix[0],oriy[0],oriz[0]]
    r_sqrt = (sqrt(pow(rotation[0], 2) + pow(rotation[1], 2) + pow(rotation[2], 2)))
    r_Norm = [i / r_sqrt for i in rotation]
    lin = [linx[0],liny[0],linz[0]]
    linear_forces = np.dot(rotation_matrix,lin)
    acc = [accx[0],accy[0],accz[0]]
    acceleration_forces = np.dot(rotation_matrix,acc)
    what_now = np.dot(rotation_matrix,r_Norm)
    b=2
def quat_to_ypr(q):
    yaw   = math.atan2(2.0 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
    pitch = -math.asin(2.0 * (q[1] * q[3] - q[0] * q[2]))
    roll  = math.atan2(2.0 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
    pitch *= 180.0 / math.pi
    yaw   *= 180.0 / math.pi
    yaw   -= -0.13  # Declination at Chandrapur, Maharashtra is - 0 degress 13 min
    roll  *= 180.0 / math.pi
    return [yaw, pitch, roll]
if __name__ =='__main__':
    path = join(DIR_CSV,"orientation_1sideonly.csv")
    solve(path)