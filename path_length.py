#!/usr/bin/env python
import sv
import vtk
import math

# ######################################
# This script is used to calculate the
# approximate length of the spline path
# provided by name. (pathName)
# ######################################

path_name = 'aorta'

# Grab the desired path from the Data Manager (dmg).
path = sv.dmg.get_path(path_name)
points = path.get_curve_points()

# Are there sufficient points in the path?
if len(points) is 0 or len(points) is 1:
    raise ValueError("Path must contain multiple points.")

# Iterate through the list, adding up the distances.
length = 0
for i in range(1, len(points)):
    # Distance formula: sqrt(dx^2 + dy^2 + dz^2)
    length += math.sqrt(math.pow(points[i][0] - points[i-1][0], 2) +
                        math.pow(points[i][1] - points[i-1][1], 2) +
                        math.pow(points[i][2] - points[i-1][2], 2))

print("[path_length] Spline Length of Path \"{0:s}\": {1:f}".format(path_name, length))
