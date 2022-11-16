import pandas as pd
import sys
from os.path import dirname, abspath, join
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np

DIR_ROOT = dirname(dirname(abspath(__file__)))
DIR_CSV = join(DIR_ROOT, "csv")
file_path = join(DIR_CSV, "throw_overhead.csv")
# 9 10 11
rows = []
acc_sum = []
lin_sum = []
times = []


def read_csv(csv_name):
    try:
        data = pd.read_csv(csv_name, sep=",", encoding='utf-8')
        return data
    except Exception:
        print("Something went wrong when trying to open the csv file!")
        sys.exit(2)


df = read_csv(file_path)
# orix,oriy,oriz,gyrox,gyroy,gyroz,linerx,linery,linerz,accx,accy,accz,gravx,gravy,gravz,temp
# DF columns
linx = df.linerx
liny = df.linery
linz = df.linerz
accx = df.accx
accy = df.accy
accz = df.accz
for i in range(len(df)):
    # lin_sum.append(abs(linx[i])+abs(liny[i])+abs(linz[i]))
    lin_sum.append(abs(linx[i] + liny[i] + linz[i]))
    # acc_sum.append(abs(accx[i])+abs(accy[i])+abs(accz[i]))
    acc_sum.append(abs(accx[i] + accy[i] + accz[i]))
    times.append(i)


def detect_peaks(data, h):
    # find all peaks (local maxima)
    # in x whose amplitude lies above 15.
    peaks, _ = find_peaks(data, height=h)
    return peaks,_
   # plt.title('Acceleration', fontsize=10)
    #plt.plot(data)
    #plt.plot(peaks, [data[j] for j in peaks], "x")
    #plt.plot(np.zeros_like(data), "--", color="gray")
    #plt.show()


def detect_lines(signal, center, sway, limit,inter_sway):
    lines = []
    current_line = []
    last_point=0
    for i in range(len(signal)):
        point = signal[i]
        # print(i)
        if in_bounds(point, center, sway):
            if last_point ==0:
                current_line.append(i)
                last_point=point
            else:
                if in_bounds(point,last_point,inter_sway):
                    current_line.append(i)
                    last_point=point
                elif len(current_line) > limit:
                    lines.append(current_line)
                    current_line = []
                    last_point=0
        elif len(current_line) > limit:
            lines.append(current_line)
            current_line = []
            last_point = 0
        else:
            current_line = []
            last_point = 0
    if len(current_line) > limit:
        lines.append(current_line)
    return lines


def in_bounds(point, center, sway):
    lower_bound = center - sway
    top_bound = center + sway
    return lower_bound <= point <= top_bound


def plot_line(each_line, axis):
    t_line_0 = np.full(len(each_line), 50)
    axis.plot(each_line, t_line_0)
def plot_points(points,axis):
    t_line_0 = np.full(len(points), 50)
    points=list(points)
    axis.plot(points, t_line_0, "o")
def plot_point(point,axis):
    axis.plot(point, 50, "x")
def get_closest_peak(point,peaks):
    smaller=[x for x in peaks if x<=point]
    if len(smaller)>0:
        return max(smaller)
    else:
        return -1
def get_next_peak(end,peaks):
    bigger=[x for x in peaks if x>=end]
    if len(bigger) > 0:
        return min(bigger)
    else:
        return -1
def find_times_of_throw(fly_lines,peaks,peak_distance):
    peak_times=set()
    last_peak=-1
    for line in fly_lines:
        start=line[0]
        end=line[-1]
        closest_peak=get_closest_peak(start,peaks)
        next_peak=get_next_peak(end,peaks)
        if closest_peak == last_peak:
            continue
        if start-closest_peak <=peak_distance:
            peak_times.add(closest_peak)
            if last_peak == -1:
                last_peak = next_peak
        if closest_peak==-1:
            continue

    return peak_times
def find_times_of_throw_individual(grav_lines,peaks):
    last_point=grav_lines[0][-1]
    higher=[x for x in peaks if x>=last_point]
    return min(higher)
peak_times,peak_heights = detect_peaks(acc_sum, 15)

gravity_line = detect_lines(acc_sum, 8, 3, 10,2)
flying_line = detect_lines(acc_sum, 1, 1, 4,1.5)

peak_times_throw=find_times_of_throw(flying_line,peak_times,5)
throw_times=find_times_of_throw_individual(gravity_line,peak_times)
fig, axs = plt.subplots(2)
axs[0].set_title('Acceleration', fontsize=10)
axs[0].plot(times, acc_sum)
axs[1].set_title('Linear Acceleration', fontsize=10)
axs[1].plot(times, lin_sum)
plot_point(throw_times,axs[0])
plot_points(peak_times_throw,axs[0])
for line in gravity_line:
    plot_line(line, axs[0])
    b = 2
for line in flying_line:
    plot_line(line, axs[0])
    b = 2

plt.show()
