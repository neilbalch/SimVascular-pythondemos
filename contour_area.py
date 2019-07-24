#!/usr/bin/env python
from sv import *
import vtk
import math
import numpy

# ######################################
# This script is used to calculate stats
# about the area of different contours,
# aka. segmentations.
# ######################################

contourName = 'aorta'
contourNameInRepo = contourName
contourIDs = range(0, 20)

# To test this script, uncomment the following lines:
# contourName = 'test'
# contourNameInRepo = contourName
# contourIDs = range(0, 1)

# Contour.SetContourKernel('Circle')
# contour = Contour.pyContour()
# GUI.ExportPathToRepos('aorta', 'aorta')
# contour.NewObject('test','aorta', 0)
# contour.SetCtrlPtsByRadius([0, 0, 0], 5)
# GUI.ImportContoursFromRepos('test', ['test'], 'test')

# Set up a list of the names to give the contour objects when copied into the repository.
repositoryContourIDs = [contourNameInRepo+"_contour_"+str(id) for id in contourIDs]

try:
  # Does this item already exist in the Repository?
  if int(Repository.Exists(repositoryContourIDs[0])):
    print("[contour_area] Contour \'" + contourNameInRepo + "\' is already included in the repo... using that.")
  else:
    GUI.ExportContourToRepos(contourName, repositoryContourIDs)

  contourArea = []
  for id in repositoryContourIDs:
    # Export the id'th contour to a VTK polyData object.
    contour = Repository.ExportToVtk(id)
    # Apply a VTK filter to locate the center of mass (average) of the points in the contour.
    com_filter = vtk.vtkCenterOfMass()
    com_filter.SetInputData(contour)
    com_filter.Update()
    center = com_filter.GetCenter()
    # Save the points in the contour to a vtkPoints object.
    contourPts = contour.GetPoints()

    # Iterate through the vtkPoints object, but not the last two (last two are
    #  control points that bung up the solution) and calculate partial areas from
    # vector cross products.
    area = 0
    for index in range(contourPts.GetNumberOfPoints() - 2):
      # Get the first point.
      point = [0.0, 0.0, 0.0]
      contourPts.GetPoint(index, point)

      # Get the second point.
      nextPoint = [0.0, 0.0, 0.0]
      # If this is the last point in the contour, (numPts - 2 - 1) then grab the
      # first one to close the contour.
      if index is contourPts.GetNumberOfPoints() - 3:
        contourPts.GetPoint(0, nextPoint)
      else:
        contourPts.GetPoint(index + 1, nextPoint)

      # Calculate the vector (deltas in x, y, and z) between the center point of
      # the contour and the two points.
      vec1 = [point[0] - center[0],
              point[1] - center[1],
              point[2] - center[2]]
      vec2 = [nextPoint[0] - center[0],
              nextPoint[1] - center[1],
              nextPoint[2] - center[2]]

      # Calculate the vector cross product of the two vectors.
      crossP = [0.0, 0.0, 0.0]
      vtk.vtkMath.Cross(vec1, vec2, crossP)

      # The magnitude of the cross product is the area of the parallelogram
      # section between the two points. We take half of this value because we
      # are only interested in section that falls inside the .
      # (https://en.wikipedia.org/wiki/Cross_product#Geometric_meaning)
      # Magnitude of vector: sqrt(dx^2 + dy^2 + dz^2)
      newArea = 0.5 * math.sqrt(math.pow(crossP[0], 2) +
                          math.pow(crossP[1], 2) +
                          math.pow(crossP[2], 2))

      # Add the area of this section to the total.
      area += newArea

    # Add the area of this contour to the list.
    contourArea.append(area)

  # Log stats.
  print("[contour_area] Area statistics:")
  print("[contour_area]   Min:\t" + str(min(contourArea)))
  print("[contour_area]   Max:\t" + str(max(contourArea)))
  print("[contour_area]   Avg:\t" + str(numpy.mean(contourArea)))
  print("[contour_area]   Median:\t" + str(numpy.median(contourArea)))

  # Garbage collection.
  for id in repositoryContourIDs:
    Repository.Delete(id)

  Repository.Delete('test')
  Repository.Delete('aorta')
except Exception as e:
  print(e)
  # pass
