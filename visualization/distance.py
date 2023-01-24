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
    a, ax, start = get_hor_acc(df, index_max)
    a2, ax2 = get_ver_acc(df, index_max)
    print("start ", start)
    hor_vel = get_init_vel(a, x)
    ver_vel = get_init_vel(a2, x)


    angle = getangle(df, index_max)
    grav = 9.80665
    #height = (initial_vel * math.sin(angle)) * time_of_flight + (0.5 * grav * time_of_flight**2)
    height = get_height(df, index_max, time_of_flight)
    if height < 0:
        angle = math.pi - angle
        height = math.sqrt(height**2)
    #distance = initial_vel * math.cos(angle)*(initial_vel*math.sin(angle) + math.sqrt((initial_vel * math.sin(angle))**2)+2*grav*height)
    #distance = distance/grav
    distance = (initial_vel * math.cos(angle) * time_of_flight) + (0.5 * grav * grav * time_of_flight**2)
    distance = hor_vel * time_of_flight
    return distance

"""
    :param df: entire imu data dataframe
    :param index: index of throw at maximum acceleration
    :return:
"""
def get_height(df,index_max, time_of_flight):
    y, x = get_accel(df, index_max)
    initial_vel = get_init_vel(y, x)
    angle = getangle(df, index_max)
    grav = 9.80665
    height = (time_of_flight * (time_of_flight * grav - 2 * initial_vel * math.sin(angle))) / 2
    return height

def getangle(df, index_max):
    y, x = get_accel(df, index_max)
    a, ax, start = get_hor_acc(df, index_max)
    a2, ax2 = get_ver_acc(df, index_max)

    hor = get_init_vel(a, x)
    ver = get_init_vel(a2, x)
    hor = math.sqrt(hor**2)
    ver = math.sqrt(ver ** 2)

    hip2 = hor**2 + ver**2
    hip2 = math.sqrt(hip2)
    if hip2 == 0:
        return 6.28319
    length = hor/hip2
    angle = math.acos(length)
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
        to_seconds = df.ms[index1+x-1]
        to_seconds = to_seconds/1000
        x_counter = x_counter + to_seconds
        xaxis.append(x_counter)
    return acc, xaxis

def get_hor_acc(df, index2):
    acc = []
    xaxis = []

    index1 = get_start_throw(df, index2)
    count = index2 - index1
    x_counter = 0.00
    for x in range(count):
        q, y, z = get_linear_xyz(df, index1 + x -1)

        k = math.sqrt(
            q ** 2 + y ** 2)
        acc.append(k)
    return acc, xaxis, index1

def get_ver_acc(df, index2):
    acc = []
    xaxis = []

    index1 = get_start_throw(df, index2)
    count = index2 - index1
    x_counter = 0.00
    for x in range(count):
        x, y, z = get_linear_xyz(df, index1 + x -1)

        k = math.sqrt(z**2)
        acc.append(k)
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
    g = -10
    x_counter = 0.00
    vel_dif = 1000
    vel_old = 0
    check_counter = 0
    final_index = 0
    vel = 0
    # Iterate through the previous indexes
    while index_start > 0 and check_counter < 2:
        to_seconds = df.ms[index_start]
        to_seconds = to_seconds / 1000
        x_counter = x_counter + to_seconds
        x.append(x_counter)
        q, y, z = get_linear_xyz(df, index_start)
        q1, y1, z1 = get_linear_xyz(df, index_start-1)
        k = math.sqrt(
            q ** 2 + y ** 2)
        acc.append(k)
        #if (q > 0 and q1 < 0) or (y > 0 and y1 < 0) or (y < 0 and y1 > 0) or (q < 0 and q1 > 0):
            #final_index = index_start
            #check_counter += 1
        if vel_dif <= 0.0001 and index_start + 3 < index_max:
            final_index = index_start
            check_counter += 1
       #else:
            #check_counter = 0
        vel = get_init_vel(acc, x)
        vel_dif = math.sqrt((vel_old - vel)**2)
        vel_old = vel
        # Update the current index
        index_start -= 1
    return final_index + 1



