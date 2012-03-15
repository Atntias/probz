"""
.. versionadded:: 1.1.0
   This demo depends on new features added to contourf3d.
"""
import numpy 
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y, Z = axes3d.get_test_data(0.05)
OffsetData = numpy.load('{}.npz'.format('offset'))
ax.plot_surface(OffsetData[OffsetData], rstride=8, cstride=8, alpha=0.3)


ax.set_xlabel('X')
ax.set_xlim(-40, 40)
ax.set_ylabel('Y')
ax.set_ylim(-40, 40)
ax.set_zlabel('Z')
ax.set_zlim(-100, 100)

plt.show()