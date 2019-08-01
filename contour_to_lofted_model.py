from sv import *
import sv_vis as vis
import random, os

#
# Creates a lofted solid from the provided source path with circular contours
# with radii +/- 0.25 from initial_radius.
#
# Args:
#  src_path_name (String): Name of the source path.
#  initial_radius (double): Initial "average" radius to use.
# Returns:
#  String: Name of the resulting lofted solid.

def create_solid_from_path(src_path_name, initial_radius):
    # Load in the source path and store the position points.
    path = Path.pyPath()
    path.GetObject(src_path_name)
    path_pos_points = path.GetPathPosPts()

    # Create contours from the points.
    kernel = "Circle"
    Contour.SetContourKernel(kernel)

    prev_radius = initial_radius # Last radius from which to add/subtract a random number.
    path_ctr_pds = []            # List of polydata objects created from the contours.
    # Extract every 10'th contour.
    for id in range(int(path.GetPathPtsNum() / 10)):
        contour = Contour.pyContour()

        # Create a new blank contour object.
        path_contour_name = src_path_name + "-contour" + str(id * 10)
        create_from_point = id * 10
        contour.NewObject(path_contour_name, src_path_name, create_from_point)

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

    # Resample the contour polydata objects.
    num_samples = 60  # Number of samples to take around circumference of contour?
    path_ctrs_pds_rspl = []
    for id in path_ctr_pds:
        new_id = id + "_resampled"
        path_ctrs_pds_rspl.append(new_id)
        Geom.SampleLoop(id, num_samples, new_id)

    # Loft the resampled contours.
    path_lofted_name = src_path_name + "_lofted"
    num_contours = len(path_ctrs_pds_rspl) * 4  # Including endpoints, how many contours to interpolate between the end caps.
    num_linear_pts_along_length = 120           # ?
    num_modes = 20                              # ?
    use_FFT = 0                                 # ?
    use_linear_sample_along_length = 1          # Linearly interpolate the contours see num_contours_to_loft.
    Geom.LoftSolid(path_ctrs_pds_rspl, path_lofted_name, num_samples,
                  num_contours, num_linear_pts_along_length, num_modes,
                  use_FFT, use_linear_sample_along_length)

    # Create a new solid from the lofted solid.
    Solid.SetKernel('PolyData')
    solid = Solid.pySolidModel()
    path_solid_name = src_path_name + "_solid"
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

    # solid.WriteNative(os.getcwd() + "/" + path_solid_name + ".vtp")

    return path_solid_pd_name

#
# Initialize the first path.
#

# Create new path object.
path1_name = "path1"
path1 = Path.pyPath()
path1.NewObject(path1_name)

# Give it some points.
path1.AddPoint([0.0, 0.0, 0.0])
path1.AddPoint([0.0, 0.0, 10.0])
path1.AddPoint([0.0, 0.0, 20.0])
path1.AddPoint([5.0, 0.0, 30.0])
path1.AddPoint([0.0, 0.0, 40.0])
path1.AddPoint([0.0, 0.0, 50.0])
path1.AddPoint([0.0, 0.0, 60.0])
# Generate the path from the added control points.
path1.CreatePath()

#
# Initialize the second path.
#

# Create new path object.
path2_name = "path2"
path2 = Path.pyPath()
path2.NewObject(path2_name)

# Give it some points.
path2.AddPoint([25.0, 0.0, 48.0])
path2.AddPoint([20.0, 0.0, 42.5])
path2.AddPoint([15.0, 0.0, 37.5])
path2.AddPoint([10.0, 0.0, 32.5])
path2.AddPoint([3.0, 0.0, 25.0])
# Generate the path from the added control points.
path2.CreatePath()

# Create solids from the paths.
path1_solid_name = create_solid_from_path(path1_name, 5.0)
path2_solid_name = create_solid_from_path(path2_name, 5.0)

merged_solid_name = "merged_solid"
Geom.Union(path1_solid_name, path2_solid_name, merged_solid_name)

# Render this all to a viewer.
window_name = "RAW Model"
ren1, renwin1 = vis.initRen(window_name)
# actor1 = vis.pRepos(ren, merged_solid_cleaned_name)
actor1 = vis.pRepos(ren1, merged_solid_name)
# Set the renderer to draw the solids as a wireframe.
# vis.polyDisplayWireframe(ren, merged_solid_cleaned_name)

# TODO: Figure out how to effectively smooth over the model.

merged_solid_smoothed_name = merged_solid_name + "_cleaned"
Geom.Local_laplacian_smooth(merged_solid_name, merged_solid_smoothed_name, 500, 0.04)

# Solid.SetKernel("PolyData")
# solid = Solid.pySolidModel()
# solid.NewObject(merged_solid_name)
# merged_solid_faceIDs = solid.GetFaceIDs()
# for id in range(len(merged_solid_faceIDs) - 1):
#     solid.CreateEdgeBlend(merged_solid_faceIDs[id], merged_solid_faceIDs[id + 1],
#                           0.25)

# Render this all to a viewer.
window_name = "PATCHED Model"
ren2, renwin2 = vis.initRen(window_name)
actor2 = vis.pRepos(ren2, merged_solid_smoothed_name)
# Set the renderer to draw the solids as a wireframe.
# vis.polyDisplayWireframe(ren, merged_solid_cleaned_name)

vis.interact(ren1, 15000)
vis.interact(ren2, 15000)