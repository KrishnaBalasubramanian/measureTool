import matplotlib.pyplot as plt
import numpy as np
inData = np.loadtxt('nbn tifr.csv',delimiter = ',',skiprows=100)
plt.plot(inData[:,1],inData[:,-1])
plt.show()