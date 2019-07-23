#!/usr/bin/env python
from sv import *
import vtk
import math
import numpy

# ######################################
# This script is used to calculate stats
# about the radii of different contours,
# aka. segmentations.
# ######################################

# contourName = 'aorta'
contourName = 'test'
contourNameInRepo = contourName
# contourIDs = range(0, 20)
contourIDs = range(0, 1)

Contour.SetContourKernel('Circle')
contour = Contour.pyContour()
GUI.ExportPathToRepos('aorta', 'aorta')
contour.NewObject('test','aorta', 0)
contour.SetCtrlPtsByRadius([0, 0, 0], 5)
GUI.ImportContoursFromRepos('test', ['test'], 'test')

# Set up a list of the names to give the contour objects when copied into the repository.
repositoryContourIDs = [contourNameInRepo+"_contour_"+str(id) for id in contourIDs]

try:
  # Does this item already exist in the Repository?
  if int(Repository.Exists(repositoryContourIDs[0])):
    print("[contour_radii] Contour \'" + contourNameInRepo + "\' is already included in the repo... using that.")
  else:
    GUI.ExportContourToRepos(contourName, repositoryContourIDs)

  # Calculate the centers of each contour in the segmentation group with a VTK
  # center of mass filter, then calculate the radius of the contour.
  contourRadii = []
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
    # Iterate through the list of points.
    radii = []
    for pointIndex in range(contourPts.GetNumberOfPoints()):
      # Save the point to a cordinate list.
      coord = [0.0, 0.0, 0.0]
      contourPts.GetPoint(pointIndex, coord)

      # Compute the "radius" between the current point and the center of the contour.
      # Distance formula: sqrt(dx^2 + dy^2 + dz^2)
      radii.append(math.sqrt(math.pow(coord[0] - center[0], 2) +
                             math.pow(coord[1] - center[1], 2) +
                             math.pow(coord[2] - center[2], 2)))

    # Append the average of the "radii" to the list of contour radii as the nominal radius of the current contour.
    contourRadii.append(numpy.mean(radii))

  # Log stats.
  print("[contour_radii] Radius statistics:")
  print("[contour_radii] \tMin:\t" + str(min(contourRadii)))
  print("[contour_radii] \tMax:\t" + str(max(contourRadii)))
  print("[contour_radii] \tAvg:\t" + str(numpy.mean(contourRadii)))
  print("[contour_radii] \tMedian:\t" + str(numpy.median(contourRadii)))

  # Garbage collection.
  for id in repositoryContourIDs:
    Repository.Delete(id)

  Repository.Delete('test')
  Repository.Delete('aorta')
except Exception as e:
  print(e)
  # pass
