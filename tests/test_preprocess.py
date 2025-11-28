import unittest
import main

class TestPreprocess(unittest.TestCase):

    def test_preprocess_0(self):
        PATH_LIST = []
        PARAMETERS = {}

        preprocessing_dict = main.preprocessing(path_list = PATH_LIST,
                                           parameters = PARAMETERS)
        self.assertEqual(
            preprocessing_dict,
            {},
        )

