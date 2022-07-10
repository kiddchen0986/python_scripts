import unittest
from collections import namedtuple
import sys
sys.path.append('../..')
from new_scripts.analyze_image import analyze_cap2_raw
from new_scripts.analyze_image import analyze_checkerboard_image

class TestAnalyzeImage(unittest.TestCase):
    def setUp(self):
        test_data_type = namedtuple('test_image', ['image', 'width', 'height'])
        self._cap2_image= test_data_type(image=r'test_data\20180227-172340-043_UniformityImage!60_128_4.raw', width = 60, height = 128)
        self._checkerboard_image = test_data_type(image=r'test_data\20180227-172340-043_CheckerboardImage.png', width=60, height=128)

    def test_analyze_cap2_raw(self):
        signal_strength, uniformity = analyze_cap2_raw.analyze_cap2(self._cap2_image.image, self._cap2_image.width, self._cap2_image.height)

    def test_analyze_checkerboard_image(self):
        analyze_checkerboard_image.analyze_checkerboard_image(self._checkerboard_image.image)

if __name__ == '__main__':
    unittest.main()
