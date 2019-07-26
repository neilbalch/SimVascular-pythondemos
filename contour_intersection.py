#!/usr/bin/env python
from sv import *
import vtk
import math
import numpy

# ######################################
# This script is used to calculate
# whether or not any contours on the
# same segmentation intersect.
# ######################################

contour_group_name = 'aorta'
# contour_group_name = 'test'
contour_group_name_in_repo = contour_group_name
# contour_ids = range(0, 20)
contour_ids = range(0, 3)

# To test this script, uncomment the following lines:
# PREREQUISITES: Path test must be a U curve and >= 3 points long.
# contour_group_name = 'test-contour'
# contour_group_name_in_repo = contour_group_name
# contour_ids = range(0, 1)

# path_to_import = 'test'
# path_name_in_repo = path_to_import + '-path'
# GUI.ExportPathToRepos(path_to_import, path_name_in_repo)

# kernel = 'Circle'
# Contour.SetContourKernel(kernel)
# contour = Contour.pyContour()

# name_of_obj = contour_group_name
# name_of_source_data = path_name_in_repo
# path_pt_to_use = 0
# contour.NewObject(name_of_obj, name_of_source_data, path_pt_to_use)

# center_pt = [0, 0, 0]
# radius = 50
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
repo_contour_ids = [contour_group_name_in_repo+"_contour_"+str(id) for id in contour_ids]

# Arguments:
#   polydata (vtkPolyData): Input polydata.
# Returns:
#   vtkPolyData: Converted polydata.
def convert_pts_to_mesh(polydata):
    aCellArray = vtk.vtkCellArray()

    boundary = vtk.vtkPolyData()
    boundary.SetPoints(polydata.GetPoints())
    boundary.SetPolys(aCellArray)
    delaunay = vtk.vtkDelaunay2D()
    delaunay.SetInputData(polydata)
    delaunay.SetSourceData(boundary)
    delaunay.Update()

    result_polydata = delaunay.GetOutput()

    return result_polydata

try:
    # Does this item already exist in the Repository?
    if int(Repository.Exists(repo_contour_ids[0])):
        print("[contour_intersection] Contour \'" + contour_group_name_in_repo + "\' is already included in the repo... using that.")
    else:
        GUI.ExportContourToRepos(contour_group_name, repo_contour_ids)

    # Iterate through the list of contours, comparing every contour to every
    # other contour.
    intersecting_contours = []
    for i in range(len(repo_contour_ids)):
        for j in range(i + 1, len(repo_contour_ids)):
            # Export the i'th and j'th contour to a VTK polyData object.
            contour1 = Repository.ExportToVtk(repo_contour_ids[i])
            contour2 = Repository.ExportToVtk(repo_contour_ids[j])

            # Convert them to triangle meshes.
            result_polydata1 = convert_pts_to_mesh(contour1)
            result_polydata2 = convert_pts_to_mesh(contour2)

            intersection_operation = vtk.vtkIntersectionPolyDataFilter()
            intersection_operation.SetInputData(0, result_polydata1)
            intersection_operation.SetInputData(1, result_polydata2)
            intersection_operation.Update()

            num_crosses = intersection_operation.GetNumberOfIntersectionPoints()
            print("[contour_intersection] i: " + str(i) + ", j: " + str(j) + ", # of crosses: " + str(num_crosses))
            if num_crosses:
                intersecting_contours.append([i, j])

    if len(intersecting_contours) is 0:
        print("[contour_intersection] No overlapping contours!")
    else:
        print("[contour_intersection] The following contours overlap!")
        for element in intersecting_contours:
            print("[contour_intersection]\t Contours " + str(element[0]) + " and "
                  + str(element[1]) + ".")
except Exception as e:
    print("Error!" + str(e))

# Garbage collection.
for id in repo_contour_ids:
    Repository.Delete(id)
# Repository.Delete('test')
# Repository.Delete(name_of_obj)
# Repository.Delete(name_of_obj2)
