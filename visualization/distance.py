import math
import orientations
from orientations import get_linear_xyz
import numpy as np
from numpy import trapz
import pandas as pd
import sys

"""
    :param df: entire imu data dataframe
    :param index1: index of when the throw starts
    :param index2: index of when the throw ends
    :param index_max: index when the acceleration is at its peak
    :return:
"""
def throw_distance(df, index_max, time_of_flight):
    y, x = get_accel(df, index_max)
    initial_vel = get_init_vel(y, x)
    angle = getangle(df, index_max)
    grav = 9.80665
    #time_of_flight = time_of_flight/1000
    #height = (initial_vel * math.sin(angle)) * time_of_flight + (0.5 * grav * time_of_flight**2)
    height = (time_of_flight*(time_of_flight * grav - 2*initial_vel*math.sin(angle)))/2
    distance = initial_vel * math.cos(angle)*(initial_vel*math.sin(angle) + math.sqrt((initial_vel * math.sin(angle))**2)+2*grav*height)
    distance = distance/grav
    print("tof ", time_of_flight)
    print("vel ", initial_vel)
    #distance = (initial_vel * math.cos(angle) * time_of_flight) + (0.5 * grav * grav * time_of_flight**2)
    return distance

"""
    :param df: entire imu data dataframe
    :param index: index of throw at maximum acceleration
    :return:
"""
def getangle(df, index):
    x, y, z = get_linear_xyz(df, index)
    h = math.sqrt(x**2+y**2)
    v = (z*-1)-9.81
    #v = math.sqrt(v**2)
    angle = math.atan(v/h)
    return angle
"""
    :param acc: dataframe of the acceleration
    :return:
"""
def get_init_vel(acc, x):
    init_vel = trapz(acc, x=x)
    return init_vel
"""
    :param df: entire imu data dataframe
    :param index1: index of when acceleration needs to be recorded
    :param index2: index of when acceleration no longer needs to be recorded
    :return:
"""
def get_accel(df, index2):
    acc = []
    xaxis = []
    index1 = get_start_throw(df, index2)

    count = index2 - index1
    x_counter = 0.00
    for x in range(count):

        k = math.sqrt(df.accx[index1+x-1]**2+df.accy[index1+x-1]**2+df.accz[index1+x-1]**2)-9.80665
        acc.append(k)
        # time value is currently at 0.1 which mean the IMU would send the data 0.1 seconds apart, change this value if you have a more accurate time stamp.
        to_seconds = df.ms[index1+x-1]
        to_seconds = to_seconds/1000
        x_counter = x_counter + to_seconds
        xaxis.append(x_counter)
    return acc, xaxis

"""
    :param df: entire imu data dataframe
    :param index: index of throw at maximum acceleration
    :return:
"""


def get_start_throw(df, index_max):
    acc = []
    x = []
    index_start = index_max -1
    g = -9.8
    x_counter = 0.00
    vel_dif = 1000
    vel_old = 0
    print(acc)
    # Iterate through the previous indexes
    while index_start > 0:
        if ((df.accx[index_start] > g and df.accx[index_start-1] <= g) or (df.accx[index_start] < -g and df.accx[index_start-1] >= -g)) or ((df.accy[index_start] > g and df.accy[index_start-1] <= g) or (df.accy[index_start] < -g and df.accy[index_start-1] >= -g)) or ((df.accz[index_start] > g and df.accz[index_start-1] <= g) or (df.accz[index_start] < -g and df.accz[index_start-1] >= -g)):
            # If so, return the current index as the start of the throw
            return index_start
        acc.append(
            math.sqrt(df.accx[index_start] ** 2 + df.accy[index_start] ** 2 + df.accz[index_start] ** 2) - 9.80665)
        to_seconds = df.ms[index_start]
        to_seconds = to_seconds / 1000
        x_counter = x_counter + to_seconds
        x.append(x_counter)
        if vel_dif <= 0.00001 and index_start + 3 < index_max:
            print("start ", index_start)
            print("end ", index_max)
            return index_start
        vel = get_init_vel(acc, x)
        vel_dif = math.sqrt((vel_old - vel)**2)
        vel_old = vel
        # Update the current index
        index_start -= 1
    return index_start



