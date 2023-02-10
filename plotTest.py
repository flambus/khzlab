# import numpy as np
# import matplotlib.pyplot as plt
 
# # data to be plotted
# x = np.arange(1, 1100)
# print(x)
# #y = x * x
 
# # plotting
# plt.title("Line graph")
# plt.xlabel("X axis")
# plt.ylabel("Y axis")
# plt.plot(x, color ="red")
# plt.show()

import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt

#plt.axis([0, 10, 0, 1])

# for i in range(100):
#     y = np.random.random()
#     plt.scatter(i, y)
    #plt.pause(0.05)

plt.ion()
# set up the figure
#fig = plt.figure()
plt.xlabel('Time')
plt.ylabel('Value')

def pause(interval):
    backend = plt.rcParams['backend']
    if backend in matplotlib.rcsetup.interactive_bk:
        figManager = matplotlib._pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            if canvas.figure.stale:
                canvas.draw()
            canvas.start_event_loop(interval)
            return

timeX = []
pixelSums = []
timeStep = 0
cnt = 0
for i in range(80):
    timeX.append(timeStep)
    pixelSums.append(np.random.random())
    plt.plot(timeX, pixelSums)
    #ax.plot(timeX, pixelSums)
    timeStep += 1
    # plt.pause(0.05)
    pause(0.05)
    cnt += 1
    if cnt == 40:
        print('== 40')
        cnt = 0
        timeX = timeX[40:]
        pixelSums = pixelSums[40:]
        plt.clf()

plt.show(block=False)