import unittest
import main

class TestPreprocess(unittest.TestCase):

    def test_preprocess_0(self):
        preprocessing_dict = {}
        PARAMETERS = {}

        processing_dict = main.processing(preprocessing_dict = preprocessing_dict,
                                             parameters = PARAMETERS)
        self.assertEqual(
            processing_dict,
            {},
        )

