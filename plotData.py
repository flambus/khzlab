import matplotlib.pyplot as plt
import numpy as np

dataOne = [-0.00585938, -0.00878906, -0.00878906, -0.00878906, -0.00976562, -0.00683594 \
, -0.00683594, -0.00292969, -0.00292969, 0.00097656, 0.00390625, 0.\
, 0.00390625, 0.00488281, 0.00292969, 0.00195312, 0.00195312, 0.00097656\
, 0.00292969, -0.00195312, 0.00000000, -0.00097656, 0.00000000, -0.00195312\
, -0.00292969, -0.00097656, 0.00000000, -0.00488281, 0.00195312, -0.00292969\
, -0.00292969, -0.00292969, -0.00292969, -0.00097656, -0.00292969, -0.00292969\
, 0.00292969, -0.00195312, 0.00097656, 0.00000000, 0.00000000, 0.00195312\
, -0.00292969, -0.00292969, -0.00585938, -0.00488281, -0.00585938, -0.00488281\
, -0.00683594, -0.00878906, -0.00585938, -0.01074219, -0.00390625, -0.00488281\
, -0.00390625, -0.00292969, -0.00390625, -0.00195312, -0.00292969, -0.00292969\
, -0.00097656, -0.00292969, -0.00097656, 0.00195312, 0.00000000, 0.00097656\
, -0.00097656, 0.00097656, 0.00000000, -0.00292969, -0.00195312, -0.00292969\
, -0.00195312, -0.00390625, -0.00488281, -0.00585938, -0.00585938, -0.00292969\
, -0.00585938, -0.00195312, -0.00488281, -0.00097656, -0.00488281, -0.00292969\
, -0.00292969, -0.00488281, 0.00000000, -0.00390625, -0.00195312, -0.00195312\
, -0.00195312, 0.00097656, -0.00488281, -0.00390625, -0.00195312, -0.00390625\
, -0.00585938, -0.00390625, -0.00585938, -0.00390625, -0.00390625, -0.00488281\
, -0.00488281, -0.00390625, -0.00292969, -0.00195312, -0.00488281, -0.00195312\
, -0.00488281, -0.00097656, -0.00195312, -0.00097656, -0.00488281, -0.00195312\
, 0.00097656, -0.00195312, -0.00292969, 0.00000000, -0.00097656, -0.00195312\
, -0.00390625, -0.00488281, -0.00488281, -0.00097656, -0.00390625, -0.00488281\
, -0.00585938, -0.00390625, -0.00292969, -0.00292969, -0.00195312, -0.00195312\
, -0.00292969, -0.00195312, -0.00097656, 0.00000000, -0.00195312, -0.00097656\
, -0.00097656, -0.00292969, 0.00000000, -0.00390625, -0.00195312, -0.00292969\
, -0.00097656, -0.00292969, -0.00390625, -0.00390625, -0.00292969, -0.00292969\
, -0.00585938, -0.00292969, -0.00585938, -0.00390625, -0.00488281, -0.00195312\
, -0.00488281, -0.00195312, -0.00097656, -0.00097656, -0.00292969, -0.00097656\
, -0.00292969, -0.00390625, -0.00195312, -0.00390625, 0.00000000, -0.00195312\
, -0.00292969, -0.00390625, -0.00292969, -0.00488281, -0.00390625, -0.00097656\
, -0.00390625, -0.00488281, -0.00585938, -0.00195312, -0.00292969, 0.00097656\
, -0.00390625, 0.00000000, -0.00292969, -0.00390625, -0.00097656, -0.00195312\
, -0.00292969, 0.00195312, -0.00488281, 0.00097656, -0.00292969, -0.00195312\
, -0.00292969, -0.00488281, -0.00488281, -0.00292969, -0.00390625, -0.00488281\
, -0.00488281, -0.00585938, -0.0078125 , -0.00097656, -0.00488281, -0.00195312\
, -0.00097656, -0.00390625, -0.00195312, -0.00097656, 0.00000000, -0.00292969\
, -0.00292969, -0.00195312, -0.00488281, -0.00292969, -0.00292969, -0.00292969\
, -0.00195312, -0.00292969, -0.00195312, -0.00292969, -0.00488281, -0.00292969\
, -0.00390625, -0.00292969, -0.00292969, 0.00097656, -0.00488281, -0.00390625\
, -0.00488281, -0.00097656, -0.00488281, -0.00097656, -0.00097656, -0.00097656\
, 0.00000000, 0.00097656, -0.00097656, -0.00195312, -0.00195312, -0.00292969\
, -0.00195312, -0.00292969, -0.00390625, -0.00292969, -0.00390625, -0.00585938\
, -0.00390625, -0.00488281, -0.00390625, -0.00585938, -0.00292969, -0.00683594\
, -0.00488281, -0.00292969, -0.00390625, 0.00000000, -0.00292969, 0.\
, 0.00000000, -0.00195312, -0.00292969, 0.00000000, -0.00097656, 0.00195312\
, -0.00195312, -0.00097656, -0.00195312, -0.00195312, -0.00292969, -0.00195312\
, -0.00292969, -0.00195312, -0.00292969, -0.00292969, -0.00390625, -0.00292969\
, -0.00390625, -0.00390625, -0.00195312, -0.00292969, -0.00390625, -0.00097656\
, -0.00390625, -0.00585938, -0.00195312, -0.00292969, -0.00488281, -0.00195312\
, -0.00488281, -0.00585938, -0.00390625, -0.00195312, -0.00292969, -0.00585938\
, -0.00292969, -0.00488281, -0.00585938, -0.00683594, -0.00390625, -0.00390625\
, -0.00488281, -0.00390625, -0.00195312, -0.00390625, -0.00292969, -0.00292969\
, -0.00292969, -0.00292969, -0.00195312, -0.00292969, -0.00097656, -0.00585938\
, -0.00097656, 0.00000000, -0.00097656, -0.00390625, 0.00097656, -0.00195312\
, 0.00000000, -0.00292969, -0.00195312, 0.00097656, 0.00000000, -0.00097656\
, 0.00000000, -0.00292969, -0.00292969, -0.00195312, -0.00390625, -0.00390625\
, -0.00390625, -0.00488281, -0.00390625, -0.00585938, -0.00585938, -0.00390625\
, -0.00292969, -0.00585938, -0.00585938, -0.00585938, -0.00390625, -0.00292969\
, -0.00195312, -0.00488281, -0.00292969, -0.00292969, -0.00097656, -0.00390625\
, 0.00000000, -0.00292969, -0.00097656, -0.00097656, -0.00097656, -0.00195312\
, -0.00097656, -0.00097656, -0.00292969, 0.00097656, -0.00390625, 0.00097656\
, -0.00390625, -0.00097656, -0.00195312, -0.00195312, -0.00195312, -0.00195312\
, -0.00292969, -0.00292969, -0.00195312, -0.00195312, -0.00390625, -0.00195312\
, -0.00097656, -0.00488281, -0.00195312, -0.00488281, -0.00585938, -0.00195312\
, -0.00390625, -0.00390625, -0.00195312, -0.00488281, -0.00390625, -0.00488281\
, -0.00390625, -0.00390625, -0.00195312, -0.00390625, -0.00292969, -0.00097656\
, -0.00390625, -0.00195312, -0.00390625, -0.00488281, -0.00195312, -0.00488281\
, -0.00292969, -0.00195312, -0.00292969, -0.00097656, -0.00097656, -0.00390625\
, 0.00097656, -0.00195312, -0.00195312, -0.00292969, 0.00000000, -0.00292969\
, -0.00292969, -0.00097656, -0.00195312, 0.00000000, -0.00292969, -0.00390625\
, 0.00097656, -0.00488281, -0.00195312, -0.00488281, -0.00292969, -0.00292969\
, -0.00292969, -0.00390625, -0.00195312, -0.00390625, -0.00585938, -0.00195312\
, -0.00292969, -0.00390625, -0.00097656, -0.00390625, -0.00195312, -0.00292969\
, -0.00292969, -0.00195312, -0.00390625, -0.00585938, 0.00000000, -0.00195312\
, -0.00488281, -0.00195312, -0.00097656, -0.00585938, -0.00097656, -0.00390625\
, -0.00585938, -0.00292969, -0.00097656, -0.00390625, -0.00097656, -0.00390625\
, -0.00390625, -0.00195312, -0.00390625, -0.00292969, -0.00097656, -0.00488281\
, -0.00292969, -0.00195312, -0.00390625, -0.00292969, -0.00292969, -0.00390625\
, -0.00292969, -0.00585938, 0.00000000, -0.00195312, -0.00390625, -0.00292969\
, -0.00292969, -0.00195312, -0.00097656, -0.00585938, -0.00195312, -0.00292969\
, -0.00195312, -0.00488281, -0.00488281, -0.00097656, -0.00390625, -0.00585938\
, 0.00097656, -0.00683594, -0.00292969, -0.00292969, -0.00292969, -0.00292969\
, -0.00488281, -0.00195312, -0.00585938, -0.00097656, -0.00292969, -0.00097656\
, -0.00292969, -0.00195312, -0.00488281, 0.00000000, -0.00292969, -0.00097656\
, -0.00292969, 0.00000000, -0.00390625, -0.00097656, -0.00292969, -0.00390625\
, -0.00390625, -0.00292969, -0.00488281, -0.00195312, -0.00097656, -0.00488281\
, -0.00292969, -0.00195312, -0.00390625, -0.00097656, -0.00292969, -0.00195312\
, -0.00585938, -0.00292969, -0.00195312, 0.00000000, -0.00390625, -0.00195312\
, -0.00097656, -0.00488281, -0.00488281, -0.00097656, -0.00097656, -0.00195312\
, -0.00195312, -0.00292969, -0.00097656, -0.00390625, -0.00195312, -0.00390625\
, -0.00097656, -0.00585938, -0.00390625, -0.00292969, -0.00488281, -0.00195312\
, -0.00097656, -0.00390625, -0.00292969, -0.00292969, -0.00195312, -0.00097656\
, -0.00585938, -0.00195312, -0.00390625, -0.00292969, -0.00195312, -0.00488281\
, -0.00292969, -0.00390625, -0.00097656, -0.00585938, -0.00390625, -0.00292969\
, 0.00097656, -0.00488281, -0.00390625, -0.00195312, -0.00195312, -0.00488281\
, 0.00097656, -0.00390625, 0.00195312, -0.00292969, -0.00292969, -0.00292969\
, -0.00390625, 0.00000000, -0.00292969, -0.00097656, -0.00292969, -0.00390625\
, -0.00488281, -0.00097656, -0.00292969, -0.00292969, -0.00390625, -0.00195312\
, 0.00000000, -0.00292969, -0.00195312, -0.00097656, -0.00195312, -0.00390625\
, -0.00292969, -0.00195312, -0.00390625, -0.00292969, -0.00195312, -0.00195312\
, -0.00097656, -0.00292969, -0.00195312, -0.00585938, -0.00195312, -0.00195312\
, 0.00000000, -0.00390625, -0.00195312, -0.00292969, -0.00488281, -0.00292969\
, -0.00292969, -0.00488281, -0.00195312, -0.00292969, -0.00390625, -0.00292969\
, -0.00292969, -0.00097656, -0.00390625, 0.00195312, -0.00097656, -0.00195312\
, -0.00097656, -0.00390625, 0.00000000, -0.00390625, -0.00195312, -0.00195312\
, -0.00292969, -0.00195312, -0.00585938, 0.00000000, -0.00195312, -0.00097656\
, -0.00195312, -0.00292969, -0.00195312, -0.00390625, -0.00292969, -0.00292969\
, -0.00292969, -0.00292969, 0.00000000, -0.00390625, -0.00292969, -0.00195312\
, -0.00195312, -0.00195312, -0.00195312, -0.00488281, -0.00195312, -0.00488281\
, -0.00390625, -0.00292969, -0.00292969, -0.00390625, -0.00488281, -0.00292969\
, -0.00195312, -0.00292969, -0.00292969, -0.00292969, -0.00683594, -0.00292969\
, -0.00195312, -0.00488281, -0.00292969, -0.00390625, -0.00390625, -0.00097656\
, -0.00390625, -0.00292969, -0.00195312, -0.00097656, -0.00195312, -0.00585938\
, -0.00195312, 0.00000000, -0.00097656, -0.00488281, -0.00097656, -0.00292969\
, -0.00195312, -0.00097656, -0.00195312, -0.00097656, -0.00292969, -0.00292969\
, -0.00292969, -0.00390625, 0.00000000, -0.00585938, 0.00000000, -0.00097656\
, -0.00097656, -0.00390625, -0.00195312, -0.00292969, -0.00390625, -0.00195312\
, -0.00195312, -0.00390625, -0.00195312, -0.00195312, -0.00390625, -0.00488281\
, 0.00000000, -0.00390625, -0.00488281, -0.00097656, -0.00390625, -0.00390625\
, -0.00390625, -0.00097656, -0.00195312, -0.00390625, -0.00097656, -0.00195312\
, -0.00390625, -0.00195312, -0.00097656, -0.00390625, 0.00097656, -0.00488281\
, -0.00097656, -0.00097656, -0.00390625, -0.00195312, -0.00195312, -0.00195312\
, -0.00292969, -0.00292969, -0.00292969, -0.00097656, -0.00195312, -0.00390625\
, -0.00097656, -0.00585938, -0.00390625, -0.00488281, -0.00097656, -0.00390625\
, -0.00292969, -0.00488281, -0.00097656, -0.00195312, -0.00390625, -0.00292969\
, -0.00195312, -0.00488281, -0.00097656, -0.00585938, -0.00488281, -0.00292969\
, -0.00195312, -0.00195312, -0.00585938, -0.00488281, -0.00292969, -0.00390625\
, -0.00390625, -0.00390625, -0.00292969, -0.00195312, -0.00097656, -0.00292969\
, -0.00292969, -0.00292969, -0.00292969, -0.00585938, 0.00000000, -0.00390625\
, -0.00195312, -0.00097656, -0.00195312, -0.00195312, -0.00292969, -0.00292969\
, -0.00390625, -0.00585938, -0.00292969, -0.00488281, -0.00097656, -0.00488281\
, -0.00585938, -0.00195312, -0.00097656, -0.00585938, -0.00195312, 0.00000000\
, -0.00292969, -0.00292969, -0.00292969, -0.00585938, -0.00097656, -0.00683594\
, -0.00585938, -0.00292969, -0.00292969, -0.00292969, -0.00292969, -0.00390625\
, -0.00488281, -0.00292969, -0.00390625, -0.0078125 , -0.00097656, -0.00390625\
, -0.00292969, -0.00488281, -0.00097656, -0.00683594, -0.00390625, -0.00390625\
, -0.00390625, -0.00390625, -0.00195312, -0.00292969, -0.00292969, -0.00195312\
, -0.00390625, -0.00195312, -0.00097656, -0.00488281, -0.00390625, -0.00292969\
, -0.00195312, -0.00292969, -0.00195312, 0.00000000, -0.00292969, -0.00097656\
, -0.00097656, -0.00292969, -0.00292969, 0.00097656, -0.00292969, -0.00195312\
, 0.00000000, -0.00195312, -0.00390625, -0.00195312, -0.00097656, -0.00488281\
, -0.00195312, -0.00292969, -0.00292969, -0.00195312, -0.00488281, -0.00097656\
, -0.00292969, -0.00097656, -0.00195312, -0.00195312, -0.00390625, -0.00292969\
, -0.00390625, -0.00390625, -0.00195312, -0.00292969, -0.00195312, -0.00488281\
, -0.00097656, -0.00292969, -0.00488281, -0.00097656, -0.00292969, -0.00292969\
, -0.00195312, -0.00390625, -0.00390625, -0.00292969, -0.00292969, -0.00292969\
, -0.00195312, -0.00488281, -0.00195312, -0.00390625, -0.00292969, -0.00292969\
, -0.00195312, -0.00195312, -0.00292969, -0.00097656, -0.00195312, -0.00195312\
, -0.00292969, 0.00000000, -0.00097656, -0.00390625, -0.00195312, 0.00000000\
, -0.00195312, -0.00097656, -0.00488281, -0.00390625, -0.00195312, -0.00292969\
, -0.00292969, -0.00683594, -0.00292969, -0.00195312, -0.00292969, -0.00488281\
, -0.00195312, -0.00292969, -0.00195312, -0.00390625, -0.00292969, -0.00488281\
, -0.00292969, -0.00488281, -0.00292969, -0.00097656, -0.00390625, -0.00292969\
, -0.00585938, -0.00097656, -0.00390625, -0.00292969, -0.00488281, -0.00292969\
, -0.00195312, -0.00292969, -0.00488281, -0.00292969, 0.00097656, -0.00585938\
, -0.00390625, 0.00000000, 0.00000000, -0.00390625, -0.00292969, -0.00292969\
, -0.00097656, -0.00390625, -0.00292969, -0.00195312, -0.00292969, -0.00292969\
, -0.00292969, -0.00292969, -0.00292969, -0.00195312, -0.00390625, -0.00292969\
, -0.00292969, -0.00097656, -0.00488281, -0.00097656, -0.00195312, -0.00488281\
, -0.00292969, -0.00390625, -0.00488281, -0.00292969, -0.00292969, -0.00292969\
, -0.00390625, -0.00292969, -0.00195312, -0.00390625, -0.00292969, -0.00390625\
, -0.00292969, -0.00195312, -0.00488281, -0.00390625, -0.00390625, -0.00097656\
, -0.00488281, -0.00097656, -0.00097656, -0.00195312, -0.00292969, -0.00390625\
, -0.00390625, -0.00390625, -0.00390625, -0.00292969, 0.00000000, -0.00390625\
, -0.00097656, -0.00292969, -0.00292969, -0.00292969, -0.00292969, -0.00292969\
, -0.00390625, -0.00488281, -0.00390625, -0.00390625, -0.00292969, -0.00390625\
, -0.00097656, -0.00097656, -0.00390625, -0.00195312, -0.00292969, -0.00292969\
, -0.00488281, -0.00390625, -0.00292969, -0.00292969, -0.00195312, -0.00390625\
, -0.00488281, -0.00292969, -0.00292969, -0.00292969, -0.00292969, -0.00488281\
, -0.00097656, -0.00195312, -0.00683594, -0.00292969, -0.00195312, -0.00195312\
, -0.00195312, -0.00195312, -0.00097656, -0.00195312, -0.00195312, -0.00488281\
, -0.00390625, -0.00292969, -0.00195312, -0.00195312]

data = []
with open("test_0607.txt", 'r') as file:
    contents = file.read()
    lineContents = contents.split(" ")
    for c in lineContents:
        data.append(c)
#print(data)
#time_axis = range(0, len(data))
print(len(np.zeros_like(dataOne)))
plt.plot(data)
plt.show()