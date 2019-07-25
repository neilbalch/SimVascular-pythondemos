#!/usr/bin/env python
from sv import *
import vtk
import math

# ######################################
# This script is used to calculate the
# approximate length of the spline path
# provided by name. (pathName)
# ######################################

path_name = 'aorta'
# name_in_repo = 'aorta'
name_in_repo = path_name

# Add the desired path to the Repository.
try:
    # Does this item already exist in the Repository?
    if int(Repository.Exists(name_in_repo)):
        print("[path_length] Path \'" + path_name + "\' is already included in \
              the repo... using that.")
    else:
        GUI.ExportPathToRepos(path_name, name_in_repo)

    # Load in the desired path object and extract points list.
    pth = Path.pyPath()
    pth.GetObject(name_in_repo)
    points = pth.GetPathPosPts()

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

    print("[path_length] Spline Path Length: " + str(length))

    # SimVascular must have the path re-imported to view it in the GUI, even though
    # it is now in the Repository.
    GUI.ImportPathFromRepos(name_in_repo)

    # Garbage collection.
    Repository.Delete(name_in_repo)
except Exception as e:
    print(e)
    # pass
