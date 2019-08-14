import base_test

def add(a, b):
    return a + b

def divide(a, b):
    return a / b

def echo(input):
  return input

# Create the test framework.
test_name = "MyTest"
test = base_test.BaseTest(test_name)

# Add tests to the list for execution.
test.add_func_test("add(a, b)", add, [5.0, 4.0], expected_return=9.0)
test.add_func_test("add(a, b)", add, [5.0, 4.0], expected_return=10.0)
test.add_func_test("add(a, b)", add, [5.0, 4.0], expected_error=ZeroDivisionError)
test.add_func_test("add(a, b)", add, [5.0, 4.0], expected_return="hello world")
test.add_func_test("divide(a, b)", divide, [5.0, 0.0], expected_error=ZeroDivisionError)
test.add_func_test("divide(a, b)", divide, [5.0, 0.0], expected_error=None)
test_list = [1, 2, 3]
wrong_list = test_list + [4]
test.add_func_test("echo", echo, [test_list], expected_return=wrong_list)

# Run all of the tests.
test.run_tests()
