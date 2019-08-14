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

sv_test_name = "SimVascular Test"
sv_test = base_test.BaseTest(sv_test_name)

# Add tests to the list for execution.
sv_test.add_func_test("Cube surfArea", Geom.SurfArea, [cube_name_pd], expected_return=6.0)
sv_test.add_func_test("Cube bounding box", Geom.Bbox, [cube_name_pd], expected_return=[-0.5, 0.5, -0.5, 0.5, -0.5, 0.5])
# This test is expected to fail, this function call will return [0.0, 0.0, 0.0]
sv_test.add_func_test("Cube avg point", Geom.AvgPt, [cube_name_pd], expected_error=ZeroDivisionError)

# Run all of the tests.
sv_test.run_tests()
