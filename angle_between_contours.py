#!/usr/bin/env python
from sv import *
import vtk
import math
import numpy

# ######################################
# This script is used to calculate the
# angle between the planes of two
# contours. (contour_id1, contour_id2)
# ######################################

contour_group_name = 'aorta'
contour_group_name_in_repo = contour_group_name
contour_id1 = 7
contour_id2 = 17

# To test this script, uncomment the following lines:
# PREREQUISITES: Path test must be a straight line and >= 2 points long.
# contour_group_name = 'test-contour'
# contour_group_name_in_repo = contour_group_name
# contour_id1 = 0
# contour_id2 = 1

# path_to_import = 'test'
# path_name_in_repo = 'test-path'
# GUI.ExportPathToRepos(path_to_import, path_name_in_repo)

# kernel = 'Circle'
# Contour.SetContourKernel(kernel)
# contour = Contour.pyContour()

# name_of_obj = contour_group_name
# name_of_source_data = path_name_in_repo
# path_pt_to_use = 0
# contour.NewObject(name_of_obj, name_of_source_data, path_pt_to_use)

# center_pt = [0, 0, 0]
# radius = 5
# contour.SetCtrlPtsByRadius(center_pt, radius)

# contour2 = Contour.pyContour()
# name_of_obj2 = contour_group_name + "2"
# path_pt_to_use = 1
# contour2.NewObject(name_of_obj2, name_of_source_data, path_pt_to_use)

# contour2.SetCtrlPtsByRadius(center_pt, radius)

# name_of_dest_obj = contour_group_name
# path_to_dest_obj = contour_group_name
# GUI.ImportContoursFromRepos(name_of_dest_obj, [name_of_obj, name_of_obj2], path_to_dest_obj)
# Repository.Delete(path_name_in_repo)

# Set up a list of the names to give the contour objects when copied into the repository.
repo_contour_ids = [contour_group_name_in_repo+"_contour_"+str(id) for id in
                    range(contour_id2 + 1 if contour_id2 > contour_id1 else contour_id1 + 1)]

# Arguments:
#   contour_name_in_repo (string): Name of the contour to process.
#   tangent_vec (List[double, 3]): List to dump the 3D tangent vector into.
def get_tangent_vec(contour_name_in_repo, tangent_vec):
    try:
        # Export the provided contour to a usable VTK PolyData object.
        contour = Repository.ExportToVtk(contour_name_in_repo)
        # Apply a VTK filter to locate the center of mass (average) of the
        # points in the first contour.
        com_filter = vtk.vtkCenterOfMass()
        com_filter.SetInputData(contour)
        com_filter.Update()
        center = com_filter.GetCenter()

        # Save the points in the first contour to a vtkPoints object and then
        # extract the first two points.
        contour_pts = contour.GetPoints()
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
    except Exception as e:
        print(e)


try:
    # Does this item already exist in the Repository?
    if int(Repository.Exists(repo_contour_ids[0])):
        print("[angle_between_contours] Contour \'" + contour_group_name_in_repo
              + "\' is already included in the repo... using that.")
    else:
        print("[angle_between_contours] Importing contours...")
        GUI.ExportContourToRepos(contour_group_name, repo_contour_ids)

    # Calculate the tangent vector to the planes of both contours.
    tangent_vec1 = [0.0, 0.0, 0.0]
    get_tangent_vec(repo_contour_ids[contour_id1], tangent_vec1)
    tangent_vec2 = [0.0, 0.0, 0.0]
    get_tangent_vec(repo_contour_ids[contour_id2], tangent_vec2)

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
except Exception as e:
    print(e)
    # pass

# Garbage collection.
for id in repo_contour_ids:
    Repository.Delete(id)
# Repository.Delete(name_of_obj)
# Repository.Delete(name_of_obj2)
