import matplotlib.pyplot as plt
import numpy as np
import math as m
import csv
from pyquaternion import Quaternion
def Rx(theta):
    return np.matrix(  [[ 1, 0           , 0           ],
                       [ 0, m.cos(theta),-m.sin(theta)],
                       [ 0, m.sin(theta), m.cos(theta)]])

def Ry(theta):
  return np.matrix([[ m.cos(theta), 0, m.sin(theta)],
                   [ 0           , 1, 0           ],
                   [-m.sin(theta), 0, m.cos(theta)]])

def Rz(theta):
  return np.matrix([[ m.cos(theta), -m.sin(theta), 0 ],
                   [ m.sin(theta), m.cos(theta) , 0 ],
                   [ 0           , 0            , 1 ]])

##^^ rotation matrixes. will problably not use
rows = []
ori = []
with open("csv\orientation1.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        rows.append(row)

for row in rows:
    ori.append((float(row[0]),float(row[1]),float(row[2])))

def u_vec_y(yaw,pitch,roll):
    x = m.cos(yaw)*m.cos(pitch)
    y = m.sin(yaw)*m.cos(pitch)
    z = m.cos(pitch)
    return (x,y,z)

#graph that bitch
fig = plt.figure(figsize=(2,2))
ax = fig.add_subplot(projection='3d')
c = 0
origin = [0,0,0]
ax.scatter(1,-1,-1,color="black")
ax.scatter(1,1,1,color="black")
ax.scatter(-1,-1,-1,color="black")
ax.scatter(1,1,-1,color="black")
ax.scatter(-1,1,-1,color="black")
ax.scatter(-1,-1,1,color="black")
ax.scatter(1,-1,1,color="black")
ax.scatter(-1,1,1,color="black")
ax.scatter(0,0,0,s=50,color='purple')

ax.plot((1,-1),(-1,-1),(-1,-1),color="blue")
ax.plot((1,1),(-1,1),(-1,-1),color="blue")
ax.plot((1,1),(-1,-1),(-1,1),color="blue")

ax.plot((-1,1),(1,1),(-1,-1),color="blue")
ax.plot((-1,-1),(1,-1),(-1,-1),color="blue")
ax.plot((-1,-1),(1,1),(-1,1),color="blue")

ax.plot((1,1),(1,1),(1,-1),color="blue")
ax.plot((1,1),(1,-1),(1,1),color="blue")
ax.plot((1,-1),(1,1),(1,1),color="blue")

ax.plot((-1,-1),(-1,-1),(1,-1),color="blue")
ax.plot((-1,1),(-1,-1),(1,1),color="blue")
ax.plot((-1,-1),(-1,1),(1,1),color="blue")

points = []
quat = []
'''
    q.w = cr * cp * cy + sr * sp * sy;
    q.x = sr * cp * cy - cr * sp * sy;
    q.y = cr * sp * cy + sr * cp * sy;
    q.z = cr * cp * sy - sr * sp * cy;
'''
# yaw-pitch-roll ???
for t_row in ori:
    c += 1
    x,y,z = u_vec_y(t_row[0],t_row[1],t_row[2])
    cr = m.cos(t_row[2]*0.5)
    sr = m.sin(t_row[2]*0.5)
    cp = m.cos(t_row[1]*0.5)
    sp = m.sin(t_row[1]*0.5)
    cy = m.cos(t_row[0]*0.5)
    sy = m.sin(t_row[0]*0.5)
    quat.append((Quaternion(cr*cp*cy+sr*sp*sy,sr*cp*cy-cr*sp*sy,cr*sp*cy+sr*cp*sy,cr*cp*sy-sr*sp*cy)))
    points.append((x,y,z))
    #ax.scatter(x,y,z)
    #ax.plot((x,0),(y,0),(z,0),color="black")
    #plotted_points.append((x,y,z))
'''p = dict(Counter(points))
for key, value in p.items():
    if value > 400:
        ax.scatter(key[0],key[1],key[2],color="red")
        ax.plot((key[0],0),(key[1],0),(key[2],0),color="black")
'''
c = 0
for q in quat:
    c += 1
    if c == 300: #plot every 300th point since python just dies if more
        c=0
        continue
    v = np.array([0.,0.,1.])
    v = q.rotate(v)
    ax.scatter(v[0],v[1],v[2],color="red")
    ax.plot((v[0],0),(v[1],0),(v[2],0),color="black")

plt.show()