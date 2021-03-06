# SimVascular-pythondemos

The scripts in this repository are demos and examples for how to use the [SimVascular](https://github.com/SimVascular/SimVascular/) Python extensibility API, which allows the end user to write scripts to automate repetitive tasks within the GUI as well as implement new functionality that isn't yet present in the GUI.

## Repository Structure

- `Testing Framework/*`: Custom unit-testing framework for the [SimVascular](https://github.com/SimVascular/SimVascular/) Python API.
  - Most run from SV CLI (`sv --python -- <file path>`), but `example_module.py` from standard Python terminal.
- `angle_between_contours.py`: Tool to calculate the angle of incidence between two contours on a single segmentation.
  - Run in SV GUI
- `contour_area.py`: Tool to calculate statistics regarding the area of contours on a segmentation.
  - Run in SV GUI
- `contour_intersection.py`: Tool to determine whether or not any contours in a segmentation intersect each other, an undesirable situation.
  - Run in SV GUI
- `contour_radii.py`: Tool to calculate statistics regarding the radius of a segmentation.
  - Run in SV GUI
- `contour_to_lofted_model.py`: Demo for how to create a simple Y lofted solid intersection from scratch. From paths to contours to lofted surface to solid to blended solids. (***CURRENTLY SEMI-UNFINISHED***)
  - Run in SV CLI (`sv --python -- <file path>`)
- `geom_check_broken_surface.py`: Demo for how to check lofted surfaces for being open surfaces, an undesirable trait.
  - Run in SV CLI (`sv --python -- <file path>`)
- `geom_stats_demo.py`: Demo of the various features offered by the `Geom.xyz` API set.
  - Run in SV CLI (`sv --python -- <file path>`)
- `mesh_stats_demo.py`: Demo of the various features offered bt the meshing API set.
  - Run in SV CLI (`sv --python -- <file path>`)
- `path_length.py`: Tool to calculate the total arc length along a centerline path.
  - Run in SV GUI
- `writeToCSV.py`: Debug tool to aid in graphing bad data.
  - Run in independent Python terminal