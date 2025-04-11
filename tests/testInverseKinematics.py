import unittest
from pygame import Vector2 as v
from monster import Limb


class TestInverseKinematics(unittest.TestCase):
    def setUp(self):
        pass

    def test_limb(self):
        res = Limb.limb(v(0, 0), v(0, 80), 57, 57)

        self.assertAlmostEqual(40, res[2].y)  # middle joint y

        self.assertAlmostEqual(315, round(res[1]))  # first rotation, inverted y in pygame

        self.assertAlmostEqual(225, round(res[3]))  # second rotation, inverted y in pygame


if __name__ == '__main__':
    unittest.main()
