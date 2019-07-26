# SimVascular-pythondemos

The scripts in this repository are demos and examples for how to use the [SimVascular](https://github.com/SimVascular/SimVascular/) Python extensibility API, which allows the end user to write scripts to automate repetive tasks within the GUI as well as implement new functionality that isn't yet present in the GUI.

## Repository Structure

- `angle_between_contours.py`: Tool to calculate the angle of incidence between two contours on a single segmentation.
- `contour_area.py`: Tool to calculate statistics regarding the area of contours on a segmentation.
- `contour_intersection.py`: Tool to determine whether or not any contours in a segmentation intersect each other, an undesirable situation.
- `contour_radii.py`: Tool to calculate statistics regarding the radius of a segmentation.
- `path_length.py`: Tool to calculate the total arc length along a centerline path.
- `writeToCSV.py`: Debug tool to aid in graphing bad data.