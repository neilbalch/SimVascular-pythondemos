from sv import *
import math
import base_test

def contour_tests(colors = True):
    path = Path.pyPath()
    path_name = "test_contour_path"
    path.NewObject(path_name)
    points = [[-1.0, 0.0, 0.0],
              [ 0.0, 0.0, 0.0],
              [ 1.0, 0.0, 0.0]]
    for point in points:
        path.AddPoint(point)
    path.CreatePath()

    contour_ids = range(0, 1)
    kernel = 'Circle'
    Contour.SetContourKernel(kernel)
    contour = Contour.pyContour()

    contour_name = 'test'
    src_data_name = path_name
    path_pt_to_use = 0
    contour.NewObject(contour_name, src_data_name, path_pt_to_use)

    center_pt = [0, 0, 0] # This is the center of the coordinate system as defined
                          # by the path points.
    radius = 5
    contour.SetCtrlPtsByRadius(center_pt, radius)

    test_name = "SimVascular Contour/Segmentation API"
    test = base_test.BaseTest(test_name)
    test.add_func_test("Contour exists", Repository.Exists, [contour_name], expected_return=True)
    area = math.pi * pow(radius, 2)
    # TODO: Why does this need to be true?
    test.set_required_decimal_accuracy(1.0)
    test.add_func_test("Area", contour.Area, [], expected_return=area)
    perimeter = 2 * math.pi * radius
    test.add_func_test("Perimeter", contour.Perimeter, [], expected_return=perimeter)
    # TODO: This API function really should return a list, not a string.
    center_str = "(" + str(points[0][0]) + "000,-" + str(points[0][1]) + "000," + str(points[0][2]) + "000)"
    test.add_func_test("Center", contour.Center, [], expected_return=center_str)

    test.run_tests()
    return test.return_test_output(use_colors=colors)

if __name__ == "__main__":
    for line in contour_tests():
        print(line)
