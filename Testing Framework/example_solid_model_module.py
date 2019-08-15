from sv import *
import math
import random
import base_test

#
# Initialize the first path.
#

# Create new path object.
path_name = "path1"
path = Path.pyPath()
path.NewObject(path_name)

# Give it some points.
path.AddPoint([0.0, 0.0, 0.0])
path.AddPoint([0.0, 0.0, 10.0])
path.AddPoint([0.0, 0.0, 20.0])
path.AddPoint([5.0, 0.0, 30.0])
path.AddPoint([0.0, 0.0, 40.0])
path.AddPoint([0.0, 0.0, 50.0])
path.AddPoint([0.0, 0.0, 60.0])
# Generate the path from the added control points.
path.CreatePath()

#
# Create the contours.
#

# Store the position points.
path_pos_points = path.GetPathPosPts()

# Create contours from the points.
kernel = "Circle"
Contour.SetContourKernel(kernel)

initial_radius = 5.0
prev_radius = initial_radius # Last radius from which to add/subtract a random number.
path_ctr_pds = []            # List of polydata objects created from the contours.
# Extract every 10'th contour.
for id in range(int(path.GetPathPtsNum() / 10)):
    contour = Contour.pyContour()

    # Create a new blank contour object.
    path_contour_name = path_name + "-contour" + str(id * 10)
    create_from_point = id * 10
    contour.NewObject(path_contour_name, path_name, create_from_point)

    # Randomize the radius and create the circular contour. Coords for the
    # center must be defined in absolute 3D space, so we must grab the real
    # position point from the path data.
    center_pt = path_pos_points[create_from_point]
    radius = prev_radius + 0.5 * (random.random() - 0.5)
    prev_radius = radius
    contour.SetCtrlPtsByRadius(center_pt, radius)

    # Extract a polydata object from the created contour and save its name in the list.
    pd_path_name = path_contour_name + "-pd"
    path_ctr_pds.append(pd_path_name)
    contour.GetPolyData(pd_path_name)

#
# Loft the contours into a surface.
#

# Resample the contour polydata objects.
num_samples = 60  # Number of samples to take around circumference of contour?
path_ctrs_pds_rspl = []
for id in path_ctr_pds:
    new_id = id + "_resampled"
    path_ctrs_pds_rspl.append(new_id)
    Geom.SampleLoop(id, num_samples, new_id)

# Loft the resampled contours.
path_lofted_name = path_name + "_lofted"
num_contours = len(path_ctrs_pds_rspl) * 4  # Including endpoints, how many contours to interpolate between the end caps.
num_linear_pts_along_length = 120           # ?
num_modes = 20                              # ?
use_FFT = 0                                 # ?
use_linear_sample_along_length = 1          # Linearly interpolate the contours see num_contours_to_loft.
Geom.LoftSolid(path_ctrs_pds_rspl, path_lofted_name, num_samples,
               num_contours, num_linear_pts_along_length, num_modes,
               use_FFT, use_linear_sample_along_length)

#
# Create a capped solid from the lofted surface.
#

# Create a new solid from the lofted surface.
Solid.SetKernel('PolyData')
solid = Solid.pySolidModel()
path_solid_name = path_name + "_solid"
solid.NewObject(path_solid_name)
# Cap the lofted volume.
path_lofted_capped_name = path_lofted_name + "_capped"
VMTKUtils.Cap_with_ids(path_lofted_name, path_lofted_capped_name, 0, 0)
solid.SetVtkPolyData(path_lofted_capped_name)
num_triangles_on_cap = 150
solid.GetBoundaryFaces(num_triangles_on_cap)

# Export the solid to a polydata object.
path_solid_pd_name = path_solid_name + "_pd"
solid.GetPolyData(path_solid_pd_name)

test = base_test.BaseTest("SimVascular Solid Model API")
test.add_func_test("Path Exists", Repository.Exists, [path_name], expected_return=True)
test.add_func_test("Loft Exists", Repository.Exists, [path_lofted_name], expected_return=True)
test.add_func_test("Capped Solid Exists", Repository.Exists, [path_lofted_capped_name], expected_return=True)
test.add_func_test("Solid Model Exists", Repository.Exists, [path_solid_name], expected_return=True)
test.add_func_test("Solid Model PolyData Exists", Repository.Exists, [path_solid_pd_name], expected_return=True)

test.run_tests()
test.print_test_output()
