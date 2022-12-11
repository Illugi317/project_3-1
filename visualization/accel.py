import pandas as pd
import sys
from os.path import dirname, abspath, join
from scipy.signal import find_peaks
from os import makedirs
import matplotlib.pyplot as plt
import numpy as np
import statistics
from classes import Throw,Roll
from rotations import detect_rolls
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

    def detect_lines(signal, center, sway, limit):
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
                    current_line.append(i)
                    last_point = point
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

    def get_peaks_between_including_second(first,second):
        qualifiers = [i for i in peak_times if i >first and i <=second]
        return qualifiers
    def next_peak_is_part_of_first_peak(first_peak,second_peak):
        if first_peak == -1 or second_peak == -1:
            return False
        first_val = acc_sum[first_peak]
        second_val = acc_sum[second_peak]
        if second_val < first_val:   # If the second peak is smaller than first
            left_bound = first_peak
            right_bound = second_peak+1
            last_val = first_val
            values_to_ignore = get_peaks_between_including_second(first_peak,second_peak)
              # If the entire slope has a downwards trend
            for i in range(right_bound-left_bound):
                current_val = acc_sum[left_bound+i]
                if left_bound+i not in values_to_ignore:
                    if last_val >= current_val:   # If all values on the slope are smaller than first
                        last_val=current_val
                    else:
                        return False
            return True
        else:
            return False
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
        processed=0
        for line in fly_lines:
            print(f"I processed {processed} line")
            processed +=1
            start = line[0]  # START OF FLAT LINE
            end = line[-1]  # END OF FLAT LINE
            closest_peak = get_closest_peak(start, peaks)  # CLOSEST PEAK BEFORE THE LINE
            curr_next = get_next_peak(end,peaks) # NEXT PEAK AFTER THE LINE
            next_is_good = True
            while next_is_good:
                if next_peak_is_part_of_first_peak(closest_peak,curr_next):
                    curr_next = get_next_peak(curr_next,peaks) # FAKE ASS NEXT PEAK FOUND
                else:
                    next_peak =curr_next
                    next_is_good = False # LEGIT NEXT PEAK FOUND
            if closest_peak == last_peak or next_peak_is_part_of_first_peak(last_peak,closest_peak):  # IF THE NEXT PEAK OF THE LAST THROW IS THE SAME PEAK THAT WE DETECT NOW, IGNORE
                continue  # THIS PART IS BASICALLY BOUNCE DETECTION
            if closest_peak == -1:  # IF CLOSEST PEAK DOESNT EXIST THEN CONTINUE
                continue
            if start - closest_peak <= peak_distance and next_peak - end <= peak_distance:  # IF THE DISTANCE BETWEEN START OF LINE AND CLOSEST PEAK IS CLOSE ENOUGH BASED ON THE MEASURE WE DID
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


    def plot_all_peaks(peak_times,peak_val,ax):
        vals = peak_val.get('peak_heights')
        for i in range(len(peak_times)):
            ax.plot(peak_times[i],vals[i],"x")



    def detect_rolls_in_air(throws,rolls):
        for t in throws:
            start_time = t.time
            end_time = t.fly_line[-1]
            roll_count = 0
            for r in rolls:
                time = r.time
                if start_time <= time <= end_time:
                    roll_count+=1
            t.set_air_rolls(roll_count)
    def detect_throws_on_floor(throws,grav_lines):
        for t in throws:
            time = t.time
            other_times = []
            for t2 in throws:
                other_times.append(t2.time)
            next_time = find_higher(time,other_times)
            if there_is_a_line_between(time,next_time,grav_lines):
                t.is_on_floor()

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
    def filter_lines(lines,maximal_derivation):
        filtered = []
        for line in lines:
            length = len(line)
            shorted_line = line[12:length-3]
            vals=[]
            for i in shorted_line:
                vals.append(acc_sum[i])
            mean = statistics.mean(vals)
            maximal = max(vals)
            minimal = min(vals)
            positive_diff = maximal-mean
            minus_diff = mean-minimal
            if positive_diff < maximal_derivation and minus_diff < maximal_derivation:
                filtered.append(line)
            #print(f" Mean value of line is at {mean}")
           # print(f"The maximal positive difference is {maximal-mean}")
            #print(f"The maximal negative difference is {mean-minimal}")
        return filtered
    peak_times, peak_heights = detect_peaks(acc_sum, 9)
    print(f"I detected peaks + {len(peak_times)}")
    gravity_lines = detect_lines(acc_sum, center=10, sway=2, limit = 30)
    flying_line = detect_lines(acc_sum, center = 1, sway = 1, limit = 15)

    gravity_lines = filter_lines(gravity_lines,0.5)


    print(f"I detected lines + {len(flying_line)}")
    throws = find_times_of_throw(flying_line, peak_times, 15)
    peak_times, peak_heights = detect_peaks(acc_sum, 15)
    if len(throws) == 0:
        flying_line = detect_lines(acc_sum, 1.5, 1.5, 10)
        throws = find_times_of_throw(flying_line, peak_times, 8)
    print("I detected throws")
    detect_throws_on_floor(throws,gravity_lines)
    for t in throws:
        t.print()
    rolls = detect_rolls(df)

    detect_rolls_in_air(throws,rolls)
    fig, axs = plt.subplots()
    axs.set_title(name, fontsize=10)
    axs.plot(times, acc_sum)
    plot_all_peaks(peak_times,peak_heights,axs)
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
    #names = ['throw_distance_chest2.csv','throw_distance_chest4.csv','throw_distance_overhead2.5.csv'
       # ,'throw_distance_overhead4.csv','throw_distance_under1.8.csv','throw_distance_under3.2.csv']
    names = ['throw_roll_on_ground.csv']
    for n in names:
        path = join(DIR_CSV, "csv_new_throws")
        path = join(path,n)
        saving_file = join(DIR_IMG,n)
        detect_throws_from_data(path, saving_file)
