import matplotlib.pyplot as plt
import numpy as np
import csv
#9 10 11
rows = []
accl = []
with open("throw_overhead.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        rows.append(row)

for row in rows:
    accl.append((float(row[9]),float(row[10]),float(row[11])))

#graph that bitch
accl_sum = [abs(x[0]+x[1]+x[2]) for x in accl]
lin_sum =  [abs(x[0]+x[1]+x[2]) for x in [(float(row[6]),float(row[7]),float(row[8])) for row in rows]]
fig, axs = plt.subplots(2)
t = np.arange(0.0, 2, 2/len(accl_sum))
axs[0].set_title('Acceleration',fontsize=10)
axs[0].plot(t,accl_sum)
axs[1].set_title('Linear Acceleration',fontsize=10)
axs[1].plot(t,lin_sum)


plt.show()