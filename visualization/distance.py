import math
import orientations
from orientations import get_linear_xyz
import numpy as np
from numpy import trapz
import pandas as pd
import sys

#df1 = pd.read_csv(r'C:\Users\Stijn\Desktop\project_3-1-main\csv\throw1.csv', sep=",", encoding='utf-8')

"""
    :param df: entire imu data dataframe
    :param index1: index of when the throw starts
    :param index2: index of when the throw ends
    :param index_max: index when the acceleration is at its peak
    :return:
"""
def throw_distance(df, index1, index2, index_max):
    y, x = get_accel(df, index1, index_max)
    initial_vel = get_init_vel(y, x)
    angle = getangle(df, index_max)
    print(angle)
    grav = 9.80665
    time_of_flight = time_of_flight*0.0185
    height = (time_of_flight*(time_of_flight * grav - 2*initial_vel*math.sin(angle)))/2
    print(height)
    distance = initial_vel * math.cos(angle)*(initial_vel*math.sin(angle) + math.sqrt((initial_vel * math.sin(angle))**2)+2*grav*height)
    distance = distance/grav
    return distance

"""
    :param df: entire imu data dataframe
    :param index: index of throw at maximum acceleration
    :return:
"""
def getangle(df, index):
    x, y, z = get_linear_xyz(df, index)
    h = math.sqrt(x**2+y**2)
    v = z-9.81
    v = math.sqrt(v**2)
    angle = math.atan(v/h)
    return angle
"""
    :param acc: dataframe of the acceleration
    :return:
"""
def get_init_vel(acc, x):
    init_vel = trapz(acc, x=x)
    print(init_vel)
    return init_vel
"""
    :param df: entire imu data dataframe
    :param index1: index of when acceleration needs to be recorded
    :param index2: index of when acceleration no longer needs to be recorded
    :return:
"""
def get_accel(df, index1, index2):
    acc = []
    xaxis = []
    count = index2 - index1
    x_counter = 0.00
    for x in range(count):

        k = math.sqrt(df.accx[index1+x-1]**2+df.accy[index1+x-1]**2+df.accz[index1+x-1]**2)-9.80665
        acc.append(k)
        # time value is currently at 0.1 which mean the IMU would send the data 0.1 seconds apart, change this value if you have a more accurate time stamp.
        x_counter = x_counter + 0.0185
        xaxis.append(x_counter)
    return acc, xaxis

#distance = throw_distance(df1,45,55,52)

#print(distance)


