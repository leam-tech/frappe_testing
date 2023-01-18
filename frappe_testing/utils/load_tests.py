import os
from unittest import TestSuite
from frappe.test_runner import _add_test

"""
Useful utility to quickly run all tests under a given python package..
Steps to use..
=> in your __init__.py file add the load_tests(loader: TestLoader, tests, pattern) method 
    accepted by the test runner
=> return the below method with the appropriate app_name and current package path (start path)
"""


def load_tests_from_package(app_name: str, start_path: str) -> TestSuite:
    test_suite = TestSuite()

    for path, folders, files in os.walk(start_path):
        for dontwalk in ('locals', '.git', 'public', '__pycache__'):
            if dontwalk in folders:
                folders.remove(dontwalk)

        folders.sort()
        files.sort()

        for filename in files:
            if filename.startswith("test_") and filename.endswith(
                    ".py") and filename != 'test_runner.py':
                _add_test(app_name, path, filename, False,
                          test_suite)

    return test_suite
