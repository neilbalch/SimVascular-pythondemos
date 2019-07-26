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
contour_group_name_in_repo = contour_group_name
contour_ids = range(0, 20)

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

    print("Num Cells: " + str(result_polydata.GetNumberOfCells()))

    # print("result_polydata:")
    # print(result_polydata)
    return result_polydata

try:
    # Does this item already exist in the Repository?
    if int(Repository.Exists(repo_contour_ids[0])):
        print("[contour_intersection] Contour \'" + contour_group_name_in_repo + "\' is already included in the repo... using that.")
    else:
        GUI.ExportContourToRepos(contour_group_name, repo_contour_ids)

    # Iterate through the list of contours, skipping the last one.
    contour_with_intersection = -1
    for i in range(len(repo_contour_ids) - 1):
        # Export the id'th and id+1'th contour to a VTK polyData object.
        contour1 = Repository.ExportToVtk(repo_contour_ids[i])
        contour2 = Repository.ExportToVtk(repo_contour_ids[i + 1])

        # Convert them to triangle meshes.
        result_polydata1 = convert_pts_to_mesh(contour1)
        result_polydata2 = convert_pts_to_mesh(contour2)

        intersection_operation = vtk.vtkIntersectionPolyDataFilter()
        intersection_operation.SetInputData(0, result_polydata1)
        intersection_operation.SetInputData(1, result_polydata2)
        intersection_operation.Update()

        print("# of crosses: " + str(intersection_operation.GetNumberOfIntersectionPoints()))


except Exception as e:
    print("Error!" + str(e))

# Garbage collection.
for id in repo_contour_ids:
    Repository.Delete(id)
# Repository.Delete('test')
