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
#  tuple(list[sv.segmentation.Circle], sv.modeling.Model): Lofted model and contours.

def create_solid_from_path(src_path, initial_radius):
    # Store the path position points.
    path_pos_points = src_path.get_curve_points()

    # Create contours from the points.
    prev_radius = initial_radius # Last radius from which to add/subtract a random number.
    contours = []                # List of contour objects created.
    contour_pds = []             # List of polydata objects created from the contours.
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
        contours.append(contour)
        contour_pds.append(contour.get_polydata())

    # Resample and align the contour polydata objects to ensure that all
    # contours contain the same quantity of points and are all rotated such that
    # the ids of each point in the contours are in the same position along the
    # contours for lofting.
    num_samples = 25    # Number of samples to take around circumference of contour.
    use_distance = True # Specify option for contour alignment.
    for index in range(0, len(contour_pds)):
        # Resample the current contour.
        contour_pds[index] = sv.geometry.interpolate_closed_curve(
                                            polydata=contour_pds[index],
                                            number_of_points=num_samples)

        # Align the current contour with the previous one, beginning with the
        # second contour.
        if not index is 0:
            contour_pds[index] = sv.geometry.align_profile(
                                                contour_pds[index - 1],
                                                contour_pds[index],
                                                use_distance)

    # Loft the contours.
    # Set loft options.
    options = sv.geometry.LoftOptions()
    # Use linear interpolation between spline sample points.
    options.interpolate_spline_points = True
    # Set the number of points to sample a spline if
    # using linear interpolation between sample points.
    options.num_spline_points = 50
    # The number of longitudinal points used to sample splines.
    options.num_long_points = 200

    # Loft solid.
    lofted_surface = sv.geometry.loft(polydata_list=contour_pds, loft_options=options)

    # Create a new solid from the lofted solid.
    lofted_model = sv.modeling.PolyData()
    lofted_model.set_surface(surface=lofted_surface)

    # Cap the lofted volume.
    capped_model_pd = sv.vmtk.cap(surface=lofted_model.get_polydata(),
                                  use_center=False)
    # capped_model_pd = sv.vmtk.cap_with_ids(surface=lofted_model.get_polydata(),
    #                                     fill_id=1, increment_id=True)
    # path_lofted_capped_name = path_lofted_name + "_capped"
    # VMTKUtils.Cap_with_ids(path_lofted_name, path_lofted_capped_name, 0, 0)
    # solid.SetVtkPolyData(path_lofted_capped_name)
    # num_triangles_on_cap = 150
    # solid.GetBoundaryFaces(num_triangles_on_cap)

    # Import the capped model PolyData into model objects.
    capped_model = sv.modeling.PolyData()
    capped_model.set_surface(surface=capped_model_pd)

    return (contours, capped_model)

#
# Initialize the first path.
#

# Create new path object and give it some points.
path1 = sv.pathplanning.Path()
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

# Create new path object and give it some points.
path2 = sv.pathplanning.Path()
path2.add_control_point([25.0, 0.0, 48.0])
path2.add_control_point([20.0, 0.0, 42.5])
path2.add_control_point([15.0, 0.0, 37.5])
path2.add_control_point([10.0, 0.0, 32.5])
path2.add_control_point([3.0, 0.0, 25.0])

#
# Create solid models from the paths and merge them together.
#

# Create solid models from the paths.
path1_contours, path1_model = create_solid_from_path(path1, 5.0)
path2_contours, path2_model = create_solid_from_path(path2, 5.0)

# Perform a boolean union to merge both models together.
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
unioned_model = modeler.union(model1=path1_model,
                              model2=path2_model)

#
# Blend faces from unioned_model together.
#

# Perform smoothing operation to round over hard edges from boolean union
# operation once supported in SV Python API.
options = sv.geometry.BlendOptions()
options.num_lapsmooth_iterations = 500

blend_radius = 1.0
blend_faces = [{'radius': blend_radius, 'face1': 1, 'face2': 2}]

blended_model_pd = sv.geometry.local_blend(surface=unioned_model,
                                           faces=blend_faces, options=options)

#
# Visualize and export generated geometry.
#

# Add all geometry objects to the SimVascular Data Manager (SV DMG) for
# results visualization.
# TODO: Figure out how to import the segmentations into the SV DMG and fix the
#       sv.dmg.add_model() method call, figure out how to add blended model.
# NOTE: These method calls will only function if a SV project is loaded or
#       initialized because they profice access to the SV DMG.
sv.dmg.add_path(name="path1", path=path1)
sv.dmg.add_path(name="path2", path=path2)
sv.dmg.add_segmentation(name="path1", path="path1", segmentations=path1_contours)
sv.dmg.add_segmentation(name="path2", path="path2", segmentations=path2_contours)
sv.dmg.add_model(name="unioned_model", model=unioned_model)
# sv.dmg.add_model(name="unioned_model", model=blended_model_pd)

# Export the solid to a polydata object written to ./unioned_model.vtp.
unioned_model.write(file_name=os.getcwd() + "/unioned_model", format="vtp")

# Render unioned surface to a viewer.
# win_width = 500
# win_height = 500
# renderer, renderer_window = graph.init_graphics(win_width, win_height)
# graph.add_geometry(renderer, unioned_model.get_polydata(),
#                    color=[0.0, 1.0, 0.0], wire=True, edges=False)
# graph.display(renderer_window)
