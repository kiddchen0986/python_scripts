import unittest

import os
import sys
sys.path.append('../..')
sys.path.append('../parse_logs')
from new_scripts.parse_logs import parse_json

class TestParseLog(unittest.TestCase):
    def setUp(self):
        self.out_data = parse_json.execute('test_data', 'parse_json_out.csv')

    def test_parse_data_is_not_none(self):
        out_data = parse_json.execute('test_data', 'parse_json_out.csv')
        self.assertIsNotNone(out_data, 'csv data is None')

    def test_csv_exist(self):
        self.assertTrue(os.path.exists('parse_json_out.csv'), "parse_json_out.csv doesn't exist")

    def test_parse_data_is_correct(self):
        for i, v in enumerate(self.out_data[1]):
            if i > 1:
                self.assertEqual(v, 'Success', 'incorrect test result')
            elif i == 1:
                self.assertEqual(v, '0E12G6G736051614', 'incorrect sensor id')
            elif i == 0:
                self.assertEqual(v, r'test_data\20180227-172340-043_result.json', 'incorrect test log')

    def tearDown(self):
        os.remove('parse_json_out.csv')

if __name__ == '__main__':
    unittest.main()
