from os.path import join
import pandas as pd
import sys
from io import StringIO
from classes import Roll

def read_csv(csv_name):
    csv_data = clean_data(csv_name)
    try:
        data = pd.read_csv(csv_data, sep=",", encoding='utf-8')
        return data
    except Exception:
        print("Something went wrong when trying to open the csv file!")
        sys.exit(2)


def clean_data(path):
    filepath = StringIO()
    with open(path, 'r', encoding='UTF-8') as f:
        for line in f.readlines():
            vals = line.split(",")
            while_length = 17
            saved = False
            if len(vals) > 17:
                saved = vals.pop()
                while_length -= 1
            while len(vals) > while_length:
                vals.pop()
            if saved:
                vals.append(saved)
            filepath.write(",".join(vals))
    filepath.seek(0)
    return filepath

def decide_walls(x, y, z):
    abs_x = abs(x)
    abs_y = abs(y)
    abs_z = abs(z)
    if abs_x > abs_y and abs_x > abs_z:
        if x > 0:
            return 5
        else:
            return 4
    elif abs_y > abs_x and abs_y > abs_z:
        if y > 0:
            return 3
        else:
            return 2
    elif abs_z > abs_y and abs_z > abs_x:
        if z > 0:
            return 1
        else:
            return 6

    return -1

def analyze_walls_print(path, name):
    df = read_csv(path)
    gravx = df.gravx
    gravy = df.gravy
    gravz = df.gravz
    main_side = []
    for i in range(len(gravz)):
        x = gravx[i]
        y = gravy[i]
        z = gravz[i]
        wall = decide_walls(x, y, z)
        main_side.append(wall)
    main_wall = max(main_side,key = main_side.count)
    print(f"FROM FILE {name} MAIN SIDE WAS {main_wall}")
def clean_walls_errors(list):
    clean_list =[]
    clean_list.append(list[0])
    for i in range(1,len(list)-1):
        last = clean_list[i-1]
        next = list[i+1]
        current = list[i]
        if current == -1:
            clean_list.append(last)
        elif last != current and next!= current:
            clean_list.append(last)
        else:
            clean_list.append(current)
    clean_list.append(list[-1])
    return clean_list
def analyze_walls(df):
    gravx = df.gravx
    gravy = df.gravy
    gravz = df.gravz
    main_side = []
    for i in range(len(gravz)):
        x = gravx[i]
        y = gravy[i]
        z = gravz[i]
        wall = decide_walls(x, y, z)
        main_side.append(wall)
    clean_sides = clean_walls_errors(main_side)
    return clean_sides
def detect_rolls(df,path=None):
    print(path)
    if path:
        df = read_csv(path)
    side = analyze_walls(df)
    current_wall=side[0]
    rolls=[]
    for i in range(len(side)):
        next_wall = side[i]
        if current_wall !=next_wall:
            new_roll = Roll(i,current_wall,next_wall)
            rolls.append(new_roll)
            current_wall = next_wall
    for r in rolls:
        r.print()
    return rolls
if __name__ == '__main__':
    paths = []
    names = ['throw_roll_on_ground.csv','throw_roll_in_air.csv']
   # for n in names:
        #path = join(DIR_CSV, "csv_new_throws")
       #path = join(path,n)
        #detect_rolls(1,path)
