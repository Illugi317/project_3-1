import pandas as pd
import sys
from os.path import dirname, abspath, join
from scipy.signal import find_peaks
from os import makedirs
import matplotlib.pyplot as plt
import numpy as np
import statistics
from classes import Throw
from distance import getangle, throw_distance, get_start_throw
from rotations import detect_rolls

DIR_ROOT = dirname(dirname(abspath(__file__)))
DIR_VISUAL = join(DIR_ROOT, "visualization")
DIR_IMG = join(DIR_VISUAL, "images")
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
        peaks, _ = find_peaks(data, height=h)
        return peaks, _

    def detect_lines_alternative(signal, center, sway, time_limit, first_point=0, inter_diff=0.5):
        """
        :param signal: The entire data we get from the accelerometer
        :param center: The center value of lines we want to find
        :param sway:  The allowed +/- values from center for lines we want to find
        :param limit: The minimum time of line ( in miliseconds)
        :return:
        """
        differences = [0]
        for i in range(1, len(signal)):
            differences.append(abs(signal[i] - signal[i - 1]))
        differences_binary = [0 if i < inter_diff else 1 for i in differences]
        lines = []
        current_line = []
        for i in range(len(signal)):
            point = differences_binary[i]
            if point == 0:
                current_line.append(first_point + i)
            elif get_time_of_line(current_line) > time_limit:
                line_val = [signal[i - first_point] for i in current_line]
                mean = sum(line_val) / len(line_val)
                if mean < center + sway:
                    lines.append(current_line)
                    current_line = []
                else:
                    current_line = []
            else:
                current_line = []
        if get_time_of_line(current_line) > time_limit:
            lines.append(current_line)
        return lines

    def detect_lines(signal, center, sway, limit, first_point=0):
        """
        :param signal: The entire data we get from the accelerometer
        :param center: The center value of lines we want to find
        :param sway:  The allowed +/- values from center for lines we want to find
        :param limit: The minimum time of line ( in miliseconds)
        :return:
        """
        lines = []
        current_line = []
        for i in range(len(signal)):
            point = signal[i]
            if in_bounds(point, center, sway):
                current_line.append(first_point + i)
            elif get_time_of_line(current_line) > limit:
                lines.append(current_line)
                current_line = []
            else:
                current_line = []
        if get_time_of_line(current_line) > limit:
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

    def plot_line(each_line, axis, color):
        """
        :param each_line: List of points on the line
        :param axis: axis to plot on
        :return: Nothing
        """
        heights = [acc_sum[i] for i in each_line]
        axis.plot(each_line, heights, color)

    def plot_throws(throws, axis):
        for t in throws:
            plot_point(t.time, axis)

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
        height = acc_sum[point]
        axis.plot(point, height, "x")

    def get_closest_peak(start, peaks):
        """
        :param start: the first point of line we are analyzing
        :param peaks: every peak we have detected
        :return: the closest peak *before* the line end
        """
        smaller = [x for x in peaks if x < start]
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

    def get_peaks_between_including_second(first, second):
        qualifiers = [i for i in peak_times if i > first and i <= second]
        return qualifiers

    def next_peak_is_part_of_first_peak(first_peak, second_peak):
        if first_peak == -1 or second_peak == -1:
            return False
        first_val = acc_sum[first_peak]
        second_val = acc_sum[second_peak]
        if second_val <= first_val:  # If the second peak is smaller than first
            if get_time_between_points(first_peak, second_peak) < 150:
                return True
            else:
                return False
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
        processed = 0
        for line in fly_lines:
            print(f"I processed {processed} line")
            processed += 1
            start = line[0]  # START OF FLAT LINE
            end = line[-1]  # END OF FLAT LINE
            closest_peak = get_closest_peak(start, peaks)  # CLOSEST PEAK BEFORE THE LINE
            peak_just_before = get_closest_peak(closest_peak, peaks)
            previous = True
            while previous:
                if next_peak_is_part_of_first_peak(peak_just_before, closest_peak):
                    closest_peak = peak_just_before
                    peak_just_before = get_closest_peak(closest_peak, peaks)
                else:
                    previous = False
            curr_next = get_next_peak(end, peaks)  # NEXT PEAK AFTER THE LINE
            next_is_good = True
            while next_is_good:
                if next_peak_is_part_of_first_peak(closest_peak, curr_next):
                    curr_next = get_next_peak(curr_next, peaks)  # ERROR PEAKFOUND
                else:
                    next_peak = curr_next
                    next_is_good = False  # LEGIT NEXT PEAK FOUND
            if closest_peak == last_peak or next_peak_is_part_of_first_peak(last_peak,
                                                                            closest_peak):  # IF THE NEXT PEAK OF THE LAST THROW IS THE SAME PEAK THAT WE DETECT NOW, IGNORE
                continue  # THIS PART IS BASICALLY BOUNCE DETECTION
            if closest_peak == -1:  # IF CLOSEST PEAK DOESNT EXIST THEN CONTINUE
                continue
            if get_time_between_points(closest_peak, start) <= peak_distance and get_time_between_points(end,
                                                                                                         next_peak) <= peak_distance:  # IF THE DISTANCE BETWEEN START OF LINE AND CLOSEST PEAK IS CLOSE ENOUGH BASED ON THE MEASURE WE DID
                time_of_throw = closest_peak
                acc_val = acc_sum[time_of_throw]
                values_at_line = [acc_sum[i] for i in line]
                mean_val = sum(values_at_line) / len(values_at_line)
                if mean_val + 8 < acc_val:
                    new_throw = Throw(acc_val, line, time_of_throw, get_time_between_points(time_of_throw, line[-1]))
                    throws.append(new_throw)
                if last_peak == -1:  # CHANGE DUMB VALUE TO NEXT PEAK IF EXISTS
                    last_peak = next_peak

        return throws

    def find_higher(time, other_times):
        bigger = [x for x in other_times if x > time]
        if len(bigger) > 0:
            return min(bigger)
        else:
            return 10000000  # DUMMY VALUE

    def there_is_a_line_between(start, end, lines):
        for l in lines:
            l_point = l[0]
            if start < l_point < end:
                return l
        return False

    def plot_all_peaks(peak_times, peak_val, ax):
        vals = peak_val.get('peak_heights')
        for i in range(len(peak_times)):
            ax.plot(peak_times[i], vals[i], "x")

    def detect_rolls_in_air(throws, rolls):
        """
        :param throws: Every throw we detected
        :param rolls: Every roll we detected
        :return:  Nothing, puts the amount of rolls that happened when the cube was flying during each throw inside of throw
        """
        for t in throws:
            start_time = t.time
            end_time = t.fly_line[-1]
            roll_count = 0
            for r in rolls:
                time = r.time
                if start_time <= time <= end_time:
                    roll_count += 1
            t.set_air_rolls(roll_count)

    def detect_throw_angle(throws):
        """
        :param throws: Every throw we detected
        :return: Nothing, puts the angle data inside of throws
        """
        for t in throws:
            time = t.time
            angle = getangle(df, time)
            t.set_angle(angle)

    def detect_throws_on_floor(throws, grav_lines):
        """
        :param throws: Every throw we detected
        :param grav_lines:  every gravity line detected
        :return: Nothing, but makes the throws be marked as the ones that ended up with cube on floor
        """
        for t in throws:
            time = t.time
            other_times = []
            for t2 in throws:
                other_times.append(t2.time)
            next_time = find_higher(time, other_times)
            result = there_is_a_line_between(time, next_time, grav_lines)
            if result != False:
                t.is_on_floor(result)

    def analyze_lines(lines, std_limit):

        good_lines = []
        for line in lines:
            values = []
            for i in line:
                values.append(acc_sum[i])
            std = statistics.stdev(values)
            if std < std_limit:
                good_lines.append(line)
        return good_lines

    def get_time_of_line(line):
        """
        :param line: flying or gravity line
        :return: The time that the cube spent during that line
        """
        if len(line) == 0:
            return 0
        return get_time_between_points(line[0], line[-1])

    def get_time_between_points(start, end):
        """
        :param start: First time point in entire data
        :param end: Second time point in entire data
        :return: The time between these points, in miliseconds
        """
        total = 0
        ms = df.ms
        for i in range(1, end + 1 - start):
            time = ms[start + i]
            total += time
        return total

    def find_possible_times_of_intense_rolls(rolls, time_between):
        """
        :param rolls: Every roll we detected
        :param time_between: Time in miliseconds between each roll to be qualified as continuous rolls
        :return: All times when the die was doing multiple rolls in a row in a short time interval determined by time_between
        """
        lines = []
        current_line = []
        for r in rolls:
            time = r.time
            if len(current_line) == 0:
                current_line.append(time)
            else:
                last = current_line[-1]
                time_diff = get_time_between_points(last, time)
                if time_diff < time_between:
                    current_line.append(time)
                else:
                    if len(current_line) > 1:
                        lines.append(current_line)
                    current_line = []
        if len(current_line) > 1:
            lines.append(current_line)
        return lines

    def find_flying_lines_from_rolling_lines(roll_lines):
        """
        :param roll_lines: The times when the cube was rolling a lot
        :return: The fly lines detected withing the rolling times of cube
        """
        total_lines = []
        for r in roll_lines:
            first = r[0] - 25
            second = r[-1] + 25
            acc_sum_here = acc_sum[first:second]
            fly_lines = detect_lines_alternative(signal=acc_sum_here, center=3, sway=3, time_limit=300,
                                                 first_point=first, inter_diff=1.5)
            total_lines.extend(fly_lines)
        return total_lines

    def vals_between(list, start, end):
        for i in list:
            if i < start or i > end:
                return False
        return True

    def add_in_order(flying, rolls):
        for lane in rolls:
            start_total = flying[0][0]
            end_total = flying[-1][-1]
            if lane[-1] < start_total:
                flying.insert(0, lane)
            elif lane[0] > end_total:
                flying.append(lane)
            else:
                start_lane = lane[0]
                end_lane = lane[-1]
                saved_index = False
                for i in range(len(flying) - 1):
                    fly = flying[i]
                    next_fly = flying[i + 1]
                    next_start = next_fly[0]
                    end_fly = fly[-1]
                    if start_lane > end_fly and next_start > end_lane:
                        saved_index = i + 1
                        break
                if saved_index:
                    flying.insert(saved_index, lane)
                else:
                    print("wtf")
        return flying

    def extend_fly_lines(flying_lines, rolling_flying_lines):
        """
        :param flying_lines: Flying times detected normally
        :param rolling_flying_lines: Flying times detected during the cube rolling
        :return: Full list of both of the lines, without multiple lines being in the same place
        """
        indexes = []
        rolls = []
        roll_indexes = []
        for i in range(len(flying_lines)):
            fly_line = flying_lines[i]
            for j in range(len(rolling_flying_lines)):
                roll_line = rolling_flying_lines[j]
                if all(item in roll_line for item in fly_line):
                    indexes.append(i)
                    rolls.append(roll_line)
                    roll_indexes.append(j)
                elif all(item in fly_line for item in roll_line):
                    roll_indexes.append(j)

        roll_indexes.reverse()
        for i in range(len(indexes)):
            index = indexes[i]
            flying_lines.pop(index)
            flying_lines.insert(index, rolls[i])

        for i in roll_indexes:
            rolling_flying_lines.pop(i)
        return add_in_order(flying_lines, rolling_flying_lines)

    def get_distance_for_throws(throws):
        for t in throws:
            time = t.time
            tof = t.tof
            distance = throw_distance(df, time, tof)
            t.set_distance(distance)

    def filter_lines(lines, maximal_deviation, cut=False):
        """
        :param lines: gravity lines we detected
        :param maximal_derivation: Maximal deviation of points on the line from the center
        ( with exclusion of first 3 points and last 3)
        Why were they excluded -> when the cube lands it has a bit of shaky data when it stops moving,
        which was usually also included in the gravity line
        And we want to only analize the data when it is 100% stopped moving
        :return: The filtered lines
        """
        filtered = []
        for line in lines:
            length = len(line)
            if cut:
                shorted_line = line[8:length - 3]
            else:
                shorted_line = line[3:length - 3]
            vals = []
            for i in shorted_line:
                vals.append(acc_sum[i])
            mean = statistics.mean(vals)
            maximal = max(vals)
            minimal = min(vals)
            positive_diff = maximal - mean
            minus_diff = mean - minimal
            if positive_diff < maximal_deviation and minus_diff < maximal_deviation:
                filtered.append(line)
        return filtered

    def get_start_of_throws(throws):
        for t in throws:
            peak = t.time
            start = get_start_throw(df, peak)
            t.set_start(start)

    def get_pictures_of_throws(throws):
        paths_list = []
        for i in range(len(throws)):
            throw = throws[i]
            line = throw.fly_line
            lower_bound = throw.start - 20
            if lower_bound < 0:
                lower_bound = 0
            grav = False
            if throw.THROW_ON_FLOOR:
                upper_bound = throw.grav_line[-1] + 20
                grav = True
            else:
                upper_bound = line[-1] + 20
            if upper_bound > len(acc_sum):
                upper_bound = len(acc_sum)
            x = range(lower_bound, upper_bound)
            y = [acc_sum[i] for i in x]
            plt.figure()
            plt.plot(x, y)
            name = f"Throw {i + 1}"
            plt.title(name, fontsize=10)
            plt.xlabel("Data points received")
            plt.ylabel("Sum of absolute acceleration values")
            plot_line(line, plt, 'y')
            plot_point(throw.time, plt)
            start_to_end = range(throw.start, throw.time + 1)
            plot_line(start_to_end, plt, 'g')
            if grav:
                plot_line(throw.grav_line, plt, 'r')
            path_to_file = name + ".png"
            plt.savefig(path_to_file, dpi=200)
            plt.clf()
            plt.close()
            paths_list.append(path_to_file)
        return paths_list

    peak_times, peak_heights = detect_peaks(acc_sum, 9)
    print(f"I detected peaks + {len(peak_times)}")
    gravity_lines = detect_lines(acc_sum, center=10, sway=2, limit=1000)
    flying_line = detect_lines_alternative(acc_sum, center=2, sway=2, time_limit=350, inter_diff=0.8)

    print(f"I detected lines + {len(flying_line)} + {len(gravity_lines)}")
    rolls = detect_rolls(df)
    # flying_line = filter_lines(flying_line,2)
    gravity_lines = filter_lines(gravity_lines, 0.5, True)

    rolling_times = find_possible_times_of_intense_rolls(rolls, 350)

    additional_fly_lines = find_flying_lines_from_rolling_lines(rolling_times)

    additional_fly_lines = analyze_lines(additional_fly_lines, 1.5)
    flying_line = extend_fly_lines(flying_line, additional_fly_lines)

    print(f"I detected lines + {len(flying_line)} + {len(gravity_lines)}")
    throws = find_times_of_throw(flying_line, peak_times, 500)
    peak_times, peak_heights = detect_peaks(acc_sum, 15)
    if len(throws) == 0:
        flying_line = detect_lines(acc_sum, 1.5, 1.5, 750)
        throws = find_times_of_throw(flying_line, peak_times, 8)
    print("I detected throws")
    detect_throws_on_floor(throws, gravity_lines)
    for t in throws:
        t.print()

    detect_rolls_in_air(throws, rolls)

    detect_throw_angle(throws)

    get_distance_for_throws(throws)
    get_start_of_throws(throws)
    throw_paths = get_pictures_of_throws(throws)
    plt.figure()
    plt.plot(times, acc_sum)
    plt.title(name, fontsize=10)
    plt.xlabel("Data points received")
    plt.ylabel("Sum of absolute acceleration values")
    plot_throws(throws, plt)
    for line in gravity_lines:
        plot_line(line, plt, 'r')
    for line in flying_line:
        plot_line(line, plt, 'y')
    path_to_file = name + ".png"
    plt.savefig(path_to_file, dpi=200)
    plt.clf()
    plt.close()
    all_pictures = [path_to_file]
    all_pictures.extend(throw_paths)
    return all_pictures, throws


if __name__ == '__main__':
    paths = []
    # names = ['throw_distance_chest2.csv','throw_distance_chest4.csv','throw_distance_overhead2.5.csv'
    # ,'throw_distance_overhead4.csv','throw_distance_under1.8.csv','throw_distance_under3.2.csv']
    names = ['throw-demo.csv']
    for n in names:
        path = join(DIR_CSV, "csv_new_throws")
        path = join(path, n)
        saving_file = join(DIR_IMG, n)
        detect_throws_from_data(path, saving_file)
