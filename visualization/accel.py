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
    plt.title('Acceleration', fontsize=10)
    plt.plot(data)
    plt.plot(peaks, [data[j] for j in peaks], "x")
    plt.plot(np.zeros_like(data), "--", color="gray")
    plt.show()


def detect_lines(signal, center, sway, limit):
    lines = []
    current_line = []
    for i in range(len(signal)):
        point = signal[i]
        # print(i)
        if in_bounds(point, center, sway):
            current_line.append(i)
        elif len(current_line) > limit:
            lines.append(current_line)
            current_line = []
        else:
            current_line = []
    if len(current_line) > limit:
        lines.append(current_line)
    return lines


def in_bounds(point, center, sway):
    lower_bound = center - sway
    top_bound = center + sway
    return point >= lower_bound and point <= top_bound


def plot_line(line, axs):
    t_line_0 = np.full(len(line), 50)
    axs.plot(line, t_line_0)


detect_peaks(acc_sum, 15)

gravity_line = detect_lines(acc_sum, 9, 2, 20)
flying_line = detect_lines(acc_sum, 1, 1, 5)

fig, axs = plt.subplots(2)
axs[0].set_title('Acceleration', fontsize=10)
axs[0].plot(times, acc_sum)
axs[1].set_title('Linear Acceleration', fontsize=10)
axs[1].plot(times, lin_sum)
for line in gravity_line:
    plot_line(line, axs[0])
    b = 2
for line in flying_line:
    plot_line(line, axs[0])
    b = 2

plt.show()
