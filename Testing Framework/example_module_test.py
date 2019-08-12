from sv import *
import base_test

def add(a, b):
    return a + b

def divide(a, b):
    return a / b

# Create the test framework.
test_name = "MyTest"
test = base_test.BaseTest(test_name)

# Add tests to the list for execution.
test.add_func_test("add(a, b)", add, [5.0, 4.0], expected_return=9.0)
test.add_func_test("add(a, b)", add, [5.0, 4.0], expected_return=10.0)
test.add_func_test("add(a, b)", add, [5.0, 4.0], expected_error=ZeroDivisionError)
test.add_func_test("divide(a, b)", divide, [5.0, 0.0], expected_error=ZeroDivisionError)
test.add_func_test("divide(a, b)", divide, [5.0, 0.0], expected_error=None)

# Run all of the tests.
test.run_tests()

# ------------------------------
# SimVascular tests:
# ------------------------------

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
