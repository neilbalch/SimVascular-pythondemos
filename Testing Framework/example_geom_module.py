from sv import *
import base_test

cube_name = "cube"
cube_name_pd = cube_name + "_pd"
cube_size = [1.0, 1.0, 1.0]
cube_center = [0.0, 0.0, 0.0]
Solid.SetKernel('PolyData')
cube = Solid.pySolidModel()
cube.Box3d(cube_name, cube_size, cube_center)
cube.GetPolyData(cube_name_pd)

test_name = "SimVascular Geom API"
test = base_test.BaseTest(test_name)

# Add tests to the list for execution.
test.add_func_test("Cube surfArea", Geom.SurfArea, [cube_name_pd], expected_return=6.0)
test.add_func_test("Cube bounding box", Geom.Bbox, [cube_name_pd], expected_return=[-0.5, 0.5, -0.5, 0.5, -0.5, 0.5])
# This test is expected to fail, this function call will return [0.0, 0.0, 0.0]
test.add_func_test("Cube avg point", Geom.AvgPt, [cube_name_pd], expected_error=ZeroDivisionError)

# Run all of the tests.
test.run_tests()
