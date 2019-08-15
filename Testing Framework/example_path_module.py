from sv import *
import math
import base_test

def get_path_length(path_name_in_repo):
  try:
      # Load in the desired path object and extract points list.
      pth = Path.pyPath()
      pth.GetObject(path_name_in_repo)
      points = pth.GetPathPosPts()

      # Are there sufficient points in the path?
      if len(points) is 0 or len(points) is 1:
          raise ValueError("Path must contain multiple points.")

      # Iterate through the list, adding up the distances.
      length = 0
      for i in range(1, len(points)):
          # Distance formula: sqrt(dx^2 + dy^2 + dz^2)
          length += math.sqrt(math.pow(points[i][0] - points[i-1][0], 2) +
                              math.pow(points[i][1] - points[i-1][1], 2) +
                              math.pow(points[i][2] - points[i-1][2], 2))

      # print("[path_length] Spline Path Length: " + str(length))
      return length
  except Exception as e:
      # print(e)
      raise e

def remove_control_point(path_obj, index):
    path_obj.RemovePoint(index)
    return path_obj.GetControlPts()

def path_tests(colors = True):
    path = Path.pyPath()
    path_name = "test_path"
    path.NewObject(path_name)
    points = [[-1.0, 0.0, 0.0],
            [ 0.0, 0.0, 0.0],
            [ 1.0, 0.0, 0.0]]
    for point in points:
        path.AddPoint(point)
    path.CreatePath()

    test_name = "SimVascular Path API"
    test = base_test.BaseTest(test_name)
    test.add_func_test("Path exists", Repository.Exists, [path_name], expected_return=True)
    test.add_func_test("get_path_length", get_path_length, [path_name], expected_return=2.0)
    test.add_func_test("GetControlPts", path.GetControlPts, [], expected_return=points)
    new_points = points[:1] + points[2:]
    test.add_func_test("RemovePoint", remove_control_point, [path, 1], expected_return=new_points)

    test.run_tests()
    return test.return_test_output(use_colors=colors)

if __name__ == "__main__":
    for line in path_tests():
        print(line)
