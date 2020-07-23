#!/usr/bin/env python
import sv
import vtk
import math
import numpy

# ######################################
# This script is used to calculate
# whether or not any contours on the
# same segmentation intersect.
# ######################################

contour_group_name = 'aorta'
contour_ids = range(0, 39)

# PREREQUISITES: Path test must be a U curve and >= 3 points long.
# To test this script, change this to True:
test_enabled = False
if test_enabled:
    contour_group_name = 'test-seg'
    contour_ids = range(0, 3)

    path_name = "test-path"
    path = sv.pathplanning.Path()
    path.add_control_point([0.0, 0.0, 0.0])
    path.add_control_point([0.0, 0.75, 0.25])
    path.add_control_point([0.0, 1.0, 1.0])

    num_path_pts = len(path.get_curve_points())

    segmentations = [sv.segmentation.Circle(radius = 0.5,
                                            center = path.get_control_points()[0],
                                            normal = path.get_curve_tangent(0)),
                     sv.segmentation.Circle(radius = 5.0,
                                            center = path.get_control_points()[1],
                                            normal = path.get_curve_tangent(int(num_path_pts / 2))),
                     sv.segmentation.Circle(radius = 5.0,
                                            center = path.get_control_points()[2],
                                            normal = path.get_curve_tangent(int(num_path_pts - 1)))]

    sv.dmg.add_path(name=path_name, path=path)
    sv.dmg.add_segmentation(name=contour_group_name, path=path_name, segmentations=segmentations)

# Uses a Delaunay triangulation filter to divide the polydata point contour into
# a triangle mesh. (https://en.wikipedia.org/wiki/Delaunay_triangulation)
#
# Arguments:
#   polydata (vtkPolyData): Input polydata.
# Returns:
#   vtkPolyData: Converted polydata.
def convert_pts_to_mesh(polydata):
    # aCellArray = vtk.vtkCellArray()

    boundary = vtk.vtkPolyData()
    boundary.SetPoints(polydata.GetPoints())
    # boundary.SetPolys(aCellArray)

    delaunay = vtk.vtkDelaunay2D()
    delaunay.SetInputData(polydata)
    delaunay.SetSourceData(boundary)
    delaunay.Update()

    result_polydata = delaunay.GetOutput()

    return result_polydata

# Guards against unnecessary error output from vtkPointLocator:
# "vtkPointLocator (0x564b0b359900): No points to subdivide"
# TODO: Figure out why these non-fatal errors are being thrown.
vtk.vtkObject.GlobalWarningDisplayOff()

# Iterate through the list of contours, comparing every contour to every
# other contour.
intersecting_contours = []
for i in range(len(contour_ids)):
    for j in range(i + 1, len(contour_ids)):
        # Export the i'th and j'th contour to a VTK polyData object.
        contour_set = sv.dmg.get_segmentation(contour_group_name)
        contour1_pd = contour_set.get_segmentation(contour_ids[i]).get_polydata()
        contour2_pd = contour_set.get_segmentation(contour_ids[j]).get_polydata()

        # Convert them to triangle meshes.
        result_polydata1 = convert_pts_to_mesh(contour1_pd)
        result_polydata2 = convert_pts_to_mesh(contour2_pd)

        # Apply the intersection filter to detect intersections between
        # source contours.
        intersection_operation = vtk.vtkIntersectionPolyDataFilter()
        intersection_operation.SetInputData(0, result_polydata1)
        intersection_operation.SetInputData(1, result_polydata2)
        intersection_operation.Update()

        # Get the number of intersection locations, log it to the screen
        # and add intersected contours to the list.
        num_crosses = intersection_operation.GetNumberOfIntersectionPoints()
        print("[contour_intersection] contour1: " + str(i) + ", contour2: "
                + str(j) + ", num intersections: " + str(num_crosses))
        if num_crosses:
            intersecting_contours.append([i, j])

# If there were any intersections, log about it.
if len(intersecting_contours) is 0:
    print("[contour_intersection] No overlapping contours!")
else:
    print("[contour_intersection] The following (" + str(len(intersecting_contours)) + ") contour(s) overlap!")
    for element in intersecting_contours:
        print("[contour_intersection]\t - Contours " + str(element[0])
                + " and " + str(element[1]) + ".")
