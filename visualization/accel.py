import pandas as pd
import sys
from os.path import dirname, abspath, join
from scipy.signal import find_peaks
from os import makedirs
import matplotlib.pyplot as plt
import numpy as np
import statistics
from throws import Throw
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


def detect_throws_from_data(path, name):
    """
    :param path:  Path to csv file
    :param name: Name of throw ( for titling plot and such)
    :return:
    """
    acc_sum = []
    lin_sum = []
    times = []
    df = read_csv(path)
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
        return peaks, _

    def detect_lines(signal, center, sway, limit, inter_sway, std_limit):
        """
        :param signal: The entire data we get from the accelerometer
        :param center: The center value of lines we want to find
        :param sway:  The allowed +/- values from center for lines we want to find
        :param limit: The minimum length of a line detected that we qualify as a legit line ( to remove small lines which wont count)
        :param inter_sway: The allowed +/- values between each point of line, to limit lines that go up and down line crazy
        :param std_limit:  A metric checked after a line, if the std of values is above limit we dont qualify the line - > recommended around 0.5
        :return:
        """
        lines = []
        current_line = []
        last_point = 0
        for i in range(len(signal)):
            point = signal[i]
            # print(i)
            if in_bounds(point, center, sway):
                if last_point == 0:
                    current_line.append(i)
                    last_point = point
                else:
                    if in_bounds(point, last_point, inter_sway):
                        current_line.append(i)
                        last_point = point
                    elif len(current_line) > limit:
                        if analyze_lines(signal, current_line, std_limit):
                            lines.append(current_line)
                        current_line = []
                        last_point = 0
            elif len(current_line) > limit:
                if analyze_lines(signal, current_line, std_limit):
                    lines.append(current_line)
                current_line = []
                last_point = 0
            else:
                current_line = []
                last_point = 0
        if len(current_line) > limit:
            if analyze_lines(signal, current_line, std_limit):
                lines.append(current_line)
        return lines

    def in_bounds(point, center, sway):
        """
        :param point: Acceleration value of point
        :param center: center of allowed values
        :param sway: Allowed +/- bounds for values
        :return:
        """
        lower_bound = center - sway
        top_bound = center + sway
        return lower_bound <= point <= top_bound

    def plot_line(each_line, axis,height):
        """
        :param each_line: List of points on the line
        :param axis: axis to plot on
        :return: Nothing
        """
        t_line_0 = np.full(len(each_line), height)
        axis.plot(each_line, t_line_0)

    def plot_throws(throws,axis):
        for t in throws:
            plot_point(t.time,axis)
    def plot_points(points, axis):
        """
        :param points: Positions ( y / time) of points to plot
        :param axis: Axis to plot on
        :return: Nothing
        """
        t_line_0 = np.full(len(points), 50)
        points = list(points)
        axis.plot(points, t_line_0, "o")

    def plot_point(point, axis):
        """
        :param point: Position ( y / time) of point to plot
        :param axis: Axis to plot on
        :return: Nothing
        """
        height=acc_sum[point]
        axis.plot(point, height, "x")

    def get_closest_peak(start, peaks):
        """
        :param start: the first point of line we are analyzing
        :param peaks: every peak we have detected
        :return: the closest peak *before* the line end
        """
        smaller = [x for x in peaks if x <= start]
        if len(smaller) > 0:
            return max(smaller)
        else:
            return -1

    def get_next_peak(end, peaks):
        """
        :param end: the last point of a line we are analyzing
        :param peaks: every peak we have detected
        :return: the closest peak *after* the line end
        """
        bigger = [x for x in peaks if x >= end]
        if len(bigger) > 0:
            return min(bigger)
        else:
            return -1

    def find_times_of_throw(fly_lines, peaks, peak_distance):
        """
        :param fly_lines: All detected lines of flight of cube
        :param peaks:  All detected peaks
        :param peak_distance: A limit to distance between a peak and a flight line. If line is too far away from peak,
        throw is not detected
        :return:
        """
        throws = list()
        last_peak = -1  # DUMB VALUE
        for line in fly_lines:
            start = line[0]  # START OF FLAT LINE
            end = line[-1]  # END OF FLAT LINE
            closest_peak = get_closest_peak(start, peaks)  # CLOSEST PEAK BEFORE THE LINE
            next_peak = get_next_peak(end, peaks)  # NEXT PEAK AFTER THE LINE
            if closest_peak == last_peak:  # IF THE NEXT PEAK OF THE LAST THROW IS THE SAME PEAK THAT WE DETECT NOW, IGNORE
                continue  # THIS PART IS BASICALLY BOUNCE DETECTION
            if closest_peak == -1:  # IF CLOSEST PEAK DOESNT EXIST THEN CONTINUE
                continue
            if start - closest_peak <= peak_distance:  # IF THE DISTANCE BETWEEN START OF LINE AND CLOSEST PEAK IS CLOSE ENOUGH BASED ON THE MEASURE WE DID
                time_of_throw = closest_peak
                acc_val = acc_sum[time_of_throw]
                new_throw = Throw(acc_val,line,time_of_throw)
                throws.append(new_throw)
                if last_peak == -1:  # CHANGE DUMB VALUE TO NEXT PEAK IF EXISTS
                    last_peak = next_peak

        return throws

    def find_times_of_throw_individual(grav_lines, peaks):
        """
        Method for detecting throws when we have data of only 1 throw for sure ( I didnt use it in a while)
        :param grav_lines: list of gravity lines
        :param peaks: all detected peaks
        :return: the time of throw
        """
        last_point = grav_lines[0][-1]
        higher = [x for x in peaks if x >= last_point]
        return min(higher)

    def find_higher(time,other_times):
        bigger = [x for x in other_times if x > time]
        if len(bigger) > 0:
            return min(bigger)
        else:
            return 10000000 #DUMMY VALUE

    def there_is_a_line_between(start,end,lines):
        for l in lines:
            l_point = l[0]
            if start<l_point<end:
                return True
        return False
    def detect_throws_on_floor(throws,grav_lines):
        for t in throws:
            time = t.time
            other_times = []
            for t2 in throws:
                other_times.append(t2.time)
            next_time = find_higher(time,other_times)
            if there_is_a_line_between(time,next_time,grav_lines):
                t.is_on_floor()
    peak_times, peak_heights = detect_peaks(acc_sum, 15)

    def analyze_lines(points, line, std_limit):
        """
        :param points: Every point of acceleration value (y)
        :param line: A line containing every time(x) of point in it
        :param std_limit: Allowed maximal standard derivation in values in line
        :return:
        """
        values = []
        for i in line:
            values.append(points[i])
        std = statistics.stdev(values)
        if std < std_limit:
            return True
        else:
            return False

    gravity_lines = detect_lines(acc_sum, 8, 3, 10, 2, 2)
    flying_line = detect_lines(acc_sum, 1, 1, 4, 3, 0.5)

    throws = find_times_of_throw(flying_line, peak_times, 5)

    if len(throws) == 0:
        flying_line = detect_lines(acc_sum, 1.5, 1.5, 2, 2, 1)
        throws = find_times_of_throw(flying_line, peak_times, 5)
    detect_throws_on_floor(throws,gravity_lines)
    fig, axs = plt.subplots()
    axs.set_title(name, fontsize=10)
    axs.plot(times, acc_sum)

    plot_throws(throws, axs)
    for line in gravity_lines:
        plot_line(line, axs,50)
    for line in flying_line:
        plot_line(line, axs,100)
    path_to_file=name+".png"
    plt.savefig(path_to_file,dpi=200)
    return path_to_file,throws
if __name__ == '__main__':
    paths = []
    names = ['throw1.csv', 'throw2.csv', 'throw3.csv', 'throw4.csv', 'throw_overhead.csv']
    for n in names:
        path = join(DIR_CSV, n)
        saving_file = join(DIR_IMG,n)
        detect_throws_from_data(path, saving_file)
