class BaseTest:
    # name (string): Name of the instance, such as "Contour Module" or "Meshing Module".
    def __init__(self, name):
        fail_color = '\033[91m'
        pass_color = '\033[92m'
        end_color = '\033[0m'
        self.pass_text = "[ " + pass_color + "PASS" + end_color + " ] "
        self.fail_text = "[ " + fail_color +   "FAIL" + end_color + " ] "

        # List of tests to complete.
        self.tests_list = []
        self.name = name

    # Private, internal method. Try not to call externally.
    def test_func(self, visible_name, func, args_list, expected_error,
                  expected_return):
        result = None
        try:
            result = func(*args_list)
        except Exception as err:
            if type(err) == expected_error:
                return [True, visible_name + " failed as expected with error: \""
                         + str(err) + "\""]
            else:
                return [False, visible_name + " failed with: \"" + str(err)
                        + "\", when: \"" + str(expected_error) + "\" was expected!"]
        else:
            if expected_error != None:
                return [False, visible_name + " didn't fail with error: \"" +
                        str(expected_error) + "\"!"]
            elif result != expected_return:
                return [False, visible_name + " returned: \"" + str(result)
                        + "\", when: \"" + str(expected_return) + "\" was expected!"]
            else:
                return [True, visible_name + " returned: \"" + str(result)
                        + "\" as expected."]

    # Adds a function test to the list.
    # visible_name (string): Short, descriptive name for what the test does.
    #                        e.g. "divide by zero" or "add_item() no args"
    # func (function pointer): Function to run to execute the test.
    # args_list (tuple): List of arguments to pass into `func` to execute the test.
    # expected_error (Exception, optional): Is the function known to throw an error?
    # expected_return (anything): Is the function supposed to return something?
    def add_func_test(self, visible_name, func, args_list, expected_error = None,
                 expected_return = None):
        self.tests_list.append([visible_name, func, args_list, expected_error,
                                expected_return])

    # Runs the list of tests (added using self.add_func_test()).
    def run_tests(self):
        print("Running " + self.name + " tests.")
        if len(self.tests_list) is 0:
            print("There are no tests to run!")
            return

        count_failed = 0
        count_succeeded = 0
        for test_params in self.tests_list:
            result = self.test_func(*test_params)
            if result[0]:
                count_succeeded += 1
                print(self.pass_text + result[1])
            else:
                count_failed += 1
                print(self.fail_text + result[1])

        print(self.name + " tests completed: " + str(count_succeeded) + " succeeded and "
              + str(count_failed) + " failed.")

