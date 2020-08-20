import sv
import vtk
import random, os
# import graphics as graph

# ##############################################################################
# This script is a demo for how to work through the workflow of creating a path
# then creating segmentations from it and lofting the segmentations for form
# unioned models. Smoothing is a TODO and hasn't been worked out yet...
# ##############################################################################

#
# Creates a lofted solid from the provided source path with circular contours
# with radii +/- 0.25 from initial_radius.
#
# Args:
#  src_path (pathplanning.Path): Source path.
#  initial_radius (double): Initial "average" radius to use.
# Returns:
#  ModelingModel: Resulting lofted model.

def create_solid_from_path(src_path, initial_radius):
    # Load in the source path and store the position points.
    path_pos_points = src_path.get_curve_points()

    # Create contours from the points.
    prev_radius = initial_radius # Last radius from which to add/subtract a random number.
    path_ctr_pds = []            # List of polydata objects created from the contours.
    # Extract every 10'th path point and create a circular contour around it.
    for id in range(int(len(path_pos_points) / 10)):
        path_point_id = id * 10

        # Randomize the radius and create the circular contour. Coords for the
        # center must be defined in absolute 3D space, so we must grab the real
        # position point from the path data.
        radius = prev_radius + 0.5 * (random.random() - 0.5)
        prev_radius = radius

        # Create a new circular contour object.
        contour = sv.segmentation.Circle(radius = radius,
                               center = path_pos_points[path_point_id],
                               normal = src_path.get_curve_tangent(path_point_id))


        # Extract a polydata object from the created contour and save it in the list.
        path_ctr_pds.append(contour.get_polydata())

    # Resample and align the contour polydata objects to ensure that all
    # contours contain the same quantity of points and are all rotated such that
    # the ids of each point in the contours are in the same position along the
    # contours for lofting.
    num_samples = 25    # Number of samples to take around circumference of contour.
    use_distance = True # Specify option for contour alignment.
    for index in range(0, len(path_ctr_pds)):
        # Resample the current contour.
        path_ctr_pds[index] = sv.geometry.interpolate_closed_curve(
                                            polydata=path_ctr_pds[index],
                                            number_of_points=num_samples)

        # Align the current contour with the previous one, beginning with the
        # second contour.
        if not index is 0:
            path_ctr_pds[index] = sv.geometry.align_profile(
                                                path_ctr_pds[index - 1],
                                                path_ctr_pds[index],
                                                use_distance)

    # Loft the contours.
    # Set loft options.
    options = sv.geometry.LoftOptions()

    # Use linear interpolation between spline sample points.
    # loft_options.interpolate_spline_points = False
    options.interpolate_spline_points = True

    # Set the number of points to sample a spline if
    # using linear interpolation between sample points.
    options.num_spline_points = 50

    # The number of longitudinal points used to sample splines.
    options.num_long_points = 200

    # Loft solid.
    lofted_surface = sv.geometry.loft(polydata_list=path_ctr_pds, loft_options=options)

    # Create a new solid from the lofted solid.
    lofted_model = sv.modeling.PolyData()
    lofted_model.set_surface(surface=lofted_surface)

    # print("lofted_model:")
    # print(lofted_model.get_polydata())

    # Cap the lofted volume.
    capped_model_pd = sv.vmtk.cap_with_ids(surface=lofted_model.get_polydata(),
                                        fill_id=1, increment_id=True)
    # path_lofted_capped_name = path_lofted_name + "_capped"
    # VMTKUtils.Cap_with_ids(path_lofted_name, path_lofted_capped_name, 0, 0)
    # solid.SetVtkPolyData(path_lofted_capped_name)
    # num_triangles_on_cap = 150
    # solid.GetBoundaryFaces(num_triangles_on_cap)

    return capped_model_pd

#
# Initialize the first path.
#

# Create new path object.
path1 = sv.pathplanning.Path()

# Give it some points.
path1.add_control_point([0.0, 0.0, 0.0])
path1.add_control_point([0.0, 0.0, 10.0])
path1.add_control_point([0.0, 0.0, 20.0])
path1.add_control_point([5.0, 0.0, 30.0])
path1.add_control_point([0.0, 0.0, 40.0])
path1.add_control_point([0.0, 0.0, 50.0])
path1.add_control_point([0.0, 0.0, 60.0])

#
# Initialize the second path.
#

# Create new path object.
path2 = sv.pathplanning.Path()

# Give it some points.
path2.add_control_point([25.0, 0.0, 48.0])
path2.add_control_point([20.0, 0.0, 42.5])
path2.add_control_point([15.0, 0.0, 37.5])
path2.add_control_point([10.0, 0.0, 32.5])
path2.add_control_point([3.0, 0.0, 25.0])

# Create models from the paths.
path1_model_pd = create_solid_from_path(path1, 5.0)
path2_model_pd = create_solid_from_path(path2, 5.0)

# Perform a boolean union to merge both models together.
# Geom.Union(path1_solid_name, path2_solid_name, merged_solid_name)
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
unioned_model = modeler.union(model1=path1_model_pd,
                              model2=path2_model_pd)

sv.dmg.add_path(name="path1", path=path1)
sv.dmg.add_path(name="path2", path=path2)
sv.dmg.add_geometry(name="unioned_surface",
                    geometry=unioned_model.get_polydata(),
                    plugin="Mesh", node="path1")

# Export the solid to a polydata object written to ./unioned_model.vtp.
unioned_model.write(file_name=os.getcwd() + "/unioned_model",
                    format="vtp")

# Render unioned surface to a viewer.
# win_width = 500
# win_height = 500
# renderer, renderer_window = graph.init_graphics(win_width, win_height)
# graph.add_geometry(renderer, unioned_model.get_polydata(),
#                    color=[0.0, 1.0, 0.0], wire=True, edges=False)
# graph.display(renderer_window)

# TODO: Implement smoothing operation to round over hard edges from boolean
#       union operation once supported in SV Python API.
# NOTE: Below lines are code from old SV Python API, circa summer 2019 and won't
#       work anymore.
# merged_solid_smoothed_name = merged_solid_name + "_cleaned"
# Geom.Local_laplacian_smooth(merged_solid_name, merged_solid_smoothed_name, 500, 0.04)
