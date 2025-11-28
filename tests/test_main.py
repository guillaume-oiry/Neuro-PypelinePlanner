import unittest
import main

class TestPreprocess(unittest.TestCase):

    def test_preprocess_0(self):
        PATH_LIST = []
        PARAMETERS = {}

        preprocessing_dict, processing_dict, postprocessing_dict = main.main(
            path_list = PATH_LIST,
            parameters = PARAMETERS,
            apply_multiprocessing=False)

        self.assertEqual(
            (preprocessing_dict, processing_dict, postprocessing_dict),
            ({}, {}, {}),
        )

