#!/usr/bin/env python
import sv
import vtk
import math
import numpy

# ######################################
# This script is used to calculate the
# angle between the planes of two
# contours. (contour_id1, contour_id2)
# ######################################

contour_group_name = 'aorta'
contour_id1 = 7
contour_id2 = 17

# PREREQUISITES: Path test must be a straight line and >= 2 points long.
# To test this script, change this to True:
test_enabled = False
if test_enabled:
    contour_group_name = 'test-seg'
    contour_id1 = 0
    contour_id2 = 2

    path_name = "test-path"
    path = sv.pathplanning.Path()
    path.add_control_point([0.0, 0.0, 0.0])
    path.add_control_point([0.0, 0.75, 0.25])
    path.add_control_point([0.0, 1.0, 1.0])

    num_path_pts = len(path.get_curve_points())

    segmentations = [sv.segmentation.Circle(radius = 1.0,
                                            center = path.get_control_points()[0],
                                            normal = path.get_curve_tangent(0)),
                     sv.segmentation.Circle(radius = 1.0,
                                            center = path.get_control_points()[1],
                                            normal = path.get_curve_tangent(int(num_path_pts / 2))),
                     sv.segmentation.Circle(radius = 1.0,
                                            center = path.get_control_points()[2],
                                            normal = path.get_curve_tangent(int(num_path_pts - 1)))]

    sv.dmg.add_path(name=path_name, path=path)
    sv.dmg.add_segmentation(name=contour_group_name, path=path_name, segmentations=segmentations)

# Arguments:
#   contour_id (int): ID of the desired contour.
#   tangent_vec (List[double, 3]): List to dump the 3D tangent vector into.
def get_tangent_vec(contour_id, tangent_vec):
    # Export the provided contour to a usable VTK PolyData object.
    contour_set = sv.dmg.get_segmentation(contour_group_name)
    contour_pd = contour_set.get_segmentation(contour_id).get_polydata()

    # Apply a VTK filter to locate the center of mass (average) of the
    # points in the first contour.
    com_filter = vtk.vtkCenterOfMass()
    com_filter.SetInputData(contour_pd)
    com_filter.Update()
    center = com_filter.GetCenter()

    # Save the points in the first contour to a vtkPoints object and then
    # extract the first two points.
    contour_pts = contour_pd.GetPoints()
    point1 = contour_pts.GetPoint(0)
    point2 = contour_pts.GetPoint(5)

    # Calculate the vector (deltas in x, y, and z) between the center point
    # of the contour and two points on the contour.
    vec1 = [point1[0] - center[0],
            point1[1] - center[1],
            point1[2] - center[2]]
    vec2 = [point2[0] - center[0],
            point2[1] - center[1],
            point2[2] - center[2]]

    # Calculate the vector cross product of the two vectors, which is also
    # the tangent vector to the plane of the two points.
    vtk.vtkMath.Cross(vec1, vec2, tangent_vec)


# Calculate the tangent vector to the planes of both contours.
tangent_vec1 = [0.0, 0.0, 0.0]
get_tangent_vec(contour_id1, tangent_vec1)
tangent_vec2 = [0.0, 0.0, 0.0]
get_tangent_vec(contour_id2, tangent_vec2)

# Compute the angle of incidence between the two vectors.
# (https://math.stackexchange.com/questions/974178/how-to-calculate-the-angle-between-2-vectors-in-3d-space-given-a-preset-function)
magnitude1 = math.sqrt(math.pow(tangent_vec1[0], 2)
                        + math.pow(tangent_vec1[1], 2)
                        + math.pow(tangent_vec1[2], 2))
magnitude2 = math.sqrt(math.pow(tangent_vec2[0], 2)
                        + math.pow(tangent_vec2[1], 2)
                        + math.pow(tangent_vec2[2], 2))
angle = math.acos(vtk.vtkMath.Dot(tangent_vec1, tangent_vec2)
                    / (magnitude1 * magnitude2))

# Log stats.
print("[angle_between_contours] Angle measured between the contours "
        + str(contour_id1) + " and " + str(contour_id2) + ":")
print("[angle_between_contours] Angle (rad): " + str(angle))
print("[angle_between_contours] Angle (deg): " + str(math.degrees(angle)))
