#!/usr/bin/env python
import sv
import vtk
import math
import numpy

# ######################################
# This script is used to calculate stats
# about the radii of different contours,
# aka. segmentations.
# ######################################

contour_group_name = 'aorta'
contour_ids = range(0, 20)

# To test this script, change this to True:
test_enabled = False
if test_enabled:
    contour_group_name = 'test-seg'
    contour_ids = range(0, 1)

    path_name = "test-path"
    path = sv.pathplanning.Path()
    path.add_control_point([0.0, 0.0, 0.0])
    path.add_control_point([0.0, 0.0, 5.0])

    segmentations = [sv.segmentation.Circle(radius = 1.0,
                                            center = path.get_control_points()[0],
                                            normal = path.get_curve_tangent(0)),
                     sv.segmentation.Circle(radius = 1.0,
                                            center = path.get_control_points()[1],
                                            normal = path.get_curve_tangent(1))]

    sv.dmg.add_path(name=path_name, path=path)
    sv.dmg.add_segmentation(name=contour_group_name, path=path_name, segmentations=segmentations)

# Grab Contour set from the Data Manager (dmg).
contour_set = sv.dmg.get_segmentation(contour_group_name)

# Calculate the centers of each contour in the segmentation group with a VTK
# center of mass filter, then calculate the radius of the contour.
contour_radii = []
for id in contour_ids:
    # print("id: " + str(id))

    # Export the current contour to a VTK polyData object.
    contour_pd = contour_set.get_segmentation(id).get_polydata()
    # Apply a VTK filter to locate the center of mass (average) of the points in the contour.
    com_filter = vtk.vtkCenterOfMass()
    com_filter.SetInputData(contour_pd)
    com_filter.Update()
    center = com_filter.GetCenter()

    # print("center: " + str(center))

    # Save the points in the contour to a vtkPoints object.
    contour_pts = contour_pd.GetPoints()
    # Iterate through the list of points, but not the last two. (last two are
    #  control points that bung up the solution)
    radii = []
    for point_index in range(contour_pts.GetNumberOfPoints() - 2):
        # print("point_index: " + str(point_index))
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
