import math

class BaseTest:
    def __init__(self, name):
        """
        Init constructor for the class.

        Args:
            name: String name of the instance, such as "Contour Module" or
                  "Meshing Module".

        Returns:
            Nothing.

        Raises:
            Nothing.
        """
        fail_color = '\033[91m'
        pass_color = '\033[92m'
        end_color = '\033[0m'
        self.pass_text = "[ " + pass_color + "PASS" + end_color + " ] "
        self.fail_text = "[ " + fail_color +   "FAIL" + end_color + " ] "

        # List of tests to complete.
        self.tests_list = []
        self.name = name
        self.required_decimal_accuracy = 0.001

    def within_required_decimal_range(self, output, expected_return):
        """
        Private, internal method. Try not to call externally.

        Args:
            output: Value to be tested.
            expected_return: Specified correct value.

        Returns:
            Tuple: [Pass/Fail boolean, message]

        Raises:
            Nothing.
        """
        return abs(expected_return - output) < self.required_decimal_accuracy

    def test_func(self, visible_name, func, args_list, expected_error,
                  expected_return):
        """
        Private, internal method. Try not to call externally.

        Args:
            visible_name: Short, descriptive name for what the test does.
                          e.g. "divide by zero" or "add_item() no args"
            func: Pointer to the function to run for execution of the test.
            args_list: Tuple of arguments to pass into `func` to execute the test.
            expected_error: Is the function known to throw an error?
            expected_return: Should the function return something?

        Returns:
            Tuple: [Pass/Fail boolean, message]

        Raises:
            Nothing.
        """
        result = None
        try:
            result = func(*args_list)
        except Exception as err:
            if type(err) == expected_error:
                return [True, visible_name + "\n\t Failed as expected with error: \""
                        + str(err) + "\""]
            else:
                return [False, visible_name + "\n\t Failed with: \"" + str(err)
                        + "\", when: \"" + str(expected_error) + "\" was expected!"]
        else:
            # If there was an expected exception...
            if expected_error != None:
                return [False, visible_name + "\n\t Didn't fail with error: \""
                        + str(expected_error) + "\", instead returning: \""
                        + str(result) + "\"!"]
            # If the actual and expected returns don't share the same type...
            elif type(result) != type(expected_return):
                return [False, visible_name + "\n\t Returned: \"" + str(result)
                        + "\" (type: \"" + str(type(result)) + "\") when: \""
                        + str(expected_return) + "\" was expected (type: \""
                        + str(type(expected_return)) + "\")!"]
            # If result is of type decimal...
            elif type(result) == type(math.pi):
                if self.within_required_decimal_range(result, expected_return):
                    return [True, visible_name + "\n\t Returned: \"" + str(result)
                            + "\", which is within +/-" + str(self.required_decimal_accuracy)
                            + " of the expected return."]
                else:
                    return [False, visible_name + "\n\t Returned: \"" + str(result)
                            + "\", which isn't within +/-"
                            + str(self.required_decimal_accuracy) + " of: \""
                            + str(expected_return) + "\"!"]
            # If result is of type list and the lists aren't of the same length...
            elif (type(result) == type([])) and (len(result) != len(expected_return)):
                return [False, visible_name + "\n\t Returned: \"" + str(result)
                        + "\" (length: \"" + str(len(result)) + "\") when: \""
                        + str(expected_return) + "\" was expected (length: \""
                        + str(len(expected_return)) + "\")!"]
            # If everything went according to plan...
            elif result == expected_return:
                return [True, visible_name + "\n\t Returned: \"" + str(result)
                        + "\" as expected."]
            # Generic error...
            else:
                return [False, visible_name + "\n\t returned: \"" + str(result)
                        + "\", when: \"" + str(expected_return) + "\" was expected!"]

    def add_func_test(self, visible_name, func, args_list, expected_error = None,
                 expected_return = None):
        """
        Method to add a test to the list for execution upon call of run_tests().

        Args:
            visible_name: Short, descriptive name for what the test does.
                          e.g. "divide by zero" or "add_item() no args"
            func: Pointer to the function to run for execution of the test.
            args_list: Tuple of arguments to pass into `func` to execute the test.
            expected_error: Is the function known to throw an error? (optional)
            expected_return: Should the function return something? (optional)

        Returns:
            Nothing.

        Raises:
            Nothing.
        """
        self.tests_list.append([visible_name, func, args_list, expected_error,
                                expected_return])

    def set_required_decimal_accuracy(self, required_accuracy):
        """
        Sets the required minimum accuracy for tests with decimal return types.

        Args:
            required_accuracy: Minimum required accuracy. e.g. 0.001 or 0.0005

        Returns:
            Nothing.

        Raises:
            Nothing.
        """
        self.required_decimal_accuracy = required_accuracy

    def run_tests(self):
        """
        Method to run all of the pre-specified tests. Prints output to the
        terminal.

        Args:
            Nothing.

        Returns:
            Nothing.

        Raises:
            Nothing.
        """
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

