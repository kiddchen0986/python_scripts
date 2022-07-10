import unittest

import os
import sys
sys.path.append('../..')
sys.path.append('../parse_logs')
from new_scripts.parse_logs import LogParser

class TestParseLog(unittest.TestCase):
    def setUp(self):
        self.parser = LogParser.LogParser_yield_report('test_data', 'parse_json_out.csv')
        self.parser.analyze()

    def test_parse_data_is_not_none(self):
        self.assertIsNotNone(self.parser.yield_data, 'yield data is None')

    def test_csv_exist(self):
        self.assertTrue(os.path.exists('parse_json_out.csv'), "parse_json_out.csv doesn't exist")

    def test_parse_data_is_correct(self):
        data = self.parser.yield_data[0]

        self.assertEqual(data['result'], 1, 'incorrect test result')
        self.assertEqual(data['sensorid'], '0E12G6G736051614', 'incorrect sensor id')
        self.assertEqual(data['Log'], r'test_data\20180227-172340-043_result.json', 'incorrect test log')

    def tearDown(self):
        os.remove('parse_json_out.csv')
        os.remove('parse_json_out_sensor_yield.csv')

if __name__ == '__main__':
    unittest.main()
