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

contour_name = 'aorta'
contour_name_in_repo = contour_name
contour_ids = range(0, 20)

# To test this script, uncomment the following lines:
# contour_name = 'test'
# contour_name_in_repo = contour_name
# contour_ids = range(0, 1)

# kernel = 'Circle'
# Contour.SetContourKernel(kernel)
# contour = Contour.pyContour()

# path_to_import = 'aorta', name_in_repo = 'aorta'
# GUI.ExportPathToRepos(path_to_import, name_in_repo))

# name_of_obj = 'test', name_of_source_data = 'aorta', path_pt_to_use = 0
# contour.NewObject(name_of_obj, name_of_source_data, path_pt_to_use)

# center_pt = [0, 0, 0], radius = 5
# contour.SetCtrlPtsByRadius(center_pt, radius)

# name_of_dest_obj = 'test', path_to_dest_obj = 'test'
# GUI.ImportContoursFromRepos(name_of_dest_obj, [name_of_obj], path_to_dest_obj)


# Set up a list of the names to give the contour objects when copied into the repository.
repository_contour_ids = [contour_name_in_repo+"_contour_"+str(id) for id in contour_ids]

try:
    # Does this item already exist in the Repository?
    if int(Repository.Exists(repository_contour_ids[0])):
        print("[contour_radii] Contour \'" + contour_name_in_repo + "\' is already included in the repo... using that.")
    else:
        GUI.ExportContourToRepos(contour_name, repository_contour_ids)

    # Calculate the centers of each contour in the segmentation group with a VTK
    # center of mass filter, then calculate the radius of the contour.
    contour_radii = []
    for id in repository_contour_ids:
        # Export the id'th contour to a VTK polyData object.
        contour = Repository.ExportToVtk(id)
        # Apply a VTK filter to locate the center of mass (average) of the points in the contour.
        com_filter = vtk.vtkCenterOfMass()
        com_filter.SetInputData(contour)
        com_filter.Update()
        center = com_filter.GetCenter()

        # Save the points in the contour to a vtkPoints object.
        contour_pts = contour.GetPoints()
        # Iterate through the list of points, but not the last two. (last two are
        #  control points that bung up the solution)
        radii = []
        for point_index in range(contour_pts.GetNumberOfPoints() - 2):
            # Save the point to a cordinate list.
            coord = [0.0, 0.0, 0.0]
            contour_pts.GetPoint(point_index, coord)

            # Compute the "radius" between the current point and the center of the contour.
            # Distance formula: sqrt(dx^2 + dy^2 + dz^2)
            radii.append(math.sqrt(math.pow(coord[0] - center[0], 2) +
                                  math.pow(coord[1] - center[1], 2) +
                                  math.pow(coord[2] - center[2], 2)))

        # Append the average of the "radii" to the list of contour radii as the nominal radius of the current contour.
        contour_radii.append(numpy.mean(radii))

    # Log stats.
    print("[contour_radii] Radius statistics:")
    print("[contour_radii]   Min:\t\t" + str(min(contour_radii)))
    print("[contour_radii]   Max:\t\t" + str(max(contour_radii)))
    print("[contour_radii]   Avg:\t\t" + str(numpy.mean(contour_radii)))
    print("[contour_radii]   Median:\t" + str(numpy.median(contour_radii)))

    # Garbage collection.
    for id in repository_contour_ids:
        Repository.Delete(id)

    Repository.Delete('test')
    Repository.Delete('aorta')
except Exception as e:
    print(e)
    # pass
