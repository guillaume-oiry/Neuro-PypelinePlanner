import unittest
import main

class TestPreprocess(unittest.TestCase):

    def test_preprocess_0(self):
        processing_dict = {}
        PARAMETERS = {}

        postprocessing_dict = main.postprocessing(processing_dict = {},
                                                parameters = PARAMETERS)
        self.assertEqual(
            postprocessing_dict,
            {},
        )

