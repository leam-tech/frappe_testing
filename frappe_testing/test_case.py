import unittest


class FrappeTestCase(unittest.TestCase):
    """
    Use this class to subclass TestCase classes to treat errors in tests as failures

    This will ensure that TearDown is run even if the test has errors
    """

    failureException = Exception
