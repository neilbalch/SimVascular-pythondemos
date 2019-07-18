#!/usr/bin/env python
from sv import *
import vtk
import math

# ######################################
# This script is used to calculate the
# approximate length of the spline path
# provided by name. (pathName)
# ######################################

pathName = 'aorta'
# nameInRepo = 'aorta'
nameInRepo = pathName

# Add the desired path to the Repository.
try:
  # Does this item already exist in the Repository?
  if int(Repository.Exists(nameInRepo)):
    print("Path \'" + pathName + "\' is already included in the repo... using that.")
  else:
    GUI.ExportPathToRepos(pathName, nameInRepo)

  # Load in the desired path object and extract points list.
  pth = Path.pyPath()
  pth.GetObject(nameInRepo)
  points = pth.GetPathPosPts()

  # print(points)

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

  print("Spline Path Length: " + str(length))
  
  # SimVascular must have the path re-imported to view it in the GUI, even though
  # it is now in the Repository.
  GUI.ImportPathFromRepos(nameInRepo)

  # Garbage collection.
  Repository.Delete(nameInRepo)
except Exception as e:
  print(e)
  # pass
