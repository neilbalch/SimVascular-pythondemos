#!/usr/bin/env python
import sv
import vtk
import math
import numpy

# ######################################
# This script is used to calculate stats
# about the area of different contours,
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

contour_area = []
for id in contour_ids:
    # Export the current contour to a VTK polyData object.
    contour_pd = contour_set.get_segmentation(id).get_polydata()
    # Apply a VTK filter to locate the center of mass (average) of the points in the contour.
    com_filter = vtk.vtkCenterOfMass()
    com_filter.SetInputData(contour_pd)
    com_filter.Update()
    center = com_filter.GetCenter()
    # Save the points in the contour to a vtkPoints object.
    contour_pts = contour_pd.GetPoints()

    # Iterate through the vtkPoints object, but not the last two (last two are
    # control points that bung up the solution) and calculate partial areas from
    # vector cross products.
    sector_area = 0
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
        # are only interested in section that falls inside the contour.
        # (https://en.wikipedia.org/wiki/Cross_product#Geometric_meaning)
        # Magnitude of vector: sqrt(dx^2 + dy^2 + dz^2)
        temp_sector_area = 0.5 * math.sqrt(math.pow(cross_p[0], 2) +
                                            math.pow(cross_p[1], 2) +
                                            math.pow(cross_p[2], 2))

        # Add the area of this section to the total.
        sector_area += temp_sector_area

    # Add the area of this contour to the list.
    contour_area.append(sector_area)

# Log stats.
print("[contour_area] Area statistics:")
print("[contour_area]   Min:\t\t" + str(min(contour_area)))
print("[contour_area]   Max:\t\t" + str(max(contour_area)))
print("[contour_area]   Avg:\t\t" + str(numpy.mean(contour_area)))
print("[contour_area]   Median:\t" + str(numpy.median(contour_area)))
