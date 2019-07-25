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
        print("[contour_area] Contour \'" + contour_name_in_repo + "\' is already included in the repo... using that.")
    else:
        GUI.ExportContourToRepos(contour_name, repository_contour_ids)

    contour_area = []
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

        # Iterate through the vtkPoints object, but not the last two (last two are
        #  control points that bung up the solution) and calculate partial areas from
        # vector cross products.
        area = 0
        for index in range(contour_pts.GetNumberOfPoints() - 2):
            # Get the first point.
            point = [0.0, 0.0, 0.0]
            contour_pts.GetPoint(index, point)

            # Get the second point.
            next_point = [0.0, 0.0, 0.0]
            # If this is the last point in the contour, (numPts - 2 - 1) then grab the
            # first one to close the contour.
            if index is contour_pts.GetNumberOfPoints() - 3:
                contour_pts.GetPoint(0, next_point)
            else:
                contour_pts.GetPoint(index + 1, next_point)

            # Calculate the vector (deltas in x, y, and z) between the center point of
            # the contour and the two points.
            vec1 = [point[0] - center[0],
                    point[1] - center[1],
                    point[2] - center[2]]
            vec2 = [next_point[0] - center[0],
                    next_point[1] - center[1],
                    next_point[2] - center[2]]

            # Calculate the vector cross product of the two vectors.
            cross_p = [0.0, 0.0, 0.0]
            vtk.vtkMath.Cross(vec1, vec2, cross_p)

            # The magnitude of the cross product is the area of the parallelogram
            # section between the two points. We take half of this value because we
            # are only interested in section that falls inside the .
            # (https://en.wikipedia.org/wiki/Cross_product#Geometric_meaning)
            # Magnitude of vector: sqrt(dx^2 + dy^2 + dz^2)
            new_area = 0.5 * math.sqrt(math.pow(cross_p[0], 2) +
                                math.pow(cross_p[1], 2) +
                                math.pow(cross_p[2], 2))

            # Add the area of this section to the total.
            area += new_area

        # Add the area of this contour to the list.
        contour_area.append(area)

    # Log stats.
    print("[contour_area] Area statistics:")
    print("[contour_area]   Min:\t\t" + str(min(contour_area)))
    print("[contour_area]   Max:\t\t" + str(max(contour_area)))
    print("[contour_area]   Avg:\t\t" + str(numpy.mean(contour_area)))
    print("[contour_area]   Median:\t" + str(numpy.median(contour_area)))

    # Garbage collection.
    for id in repository_contour_ids:
        Repository.Delete(id)

    Repository.Delete('test')
    Repository.Delete('aorta')
except Exception as e:
    print(e)
    # pass
