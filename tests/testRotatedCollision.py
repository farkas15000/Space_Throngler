import unittest
from pygame import Rect as r
from multi_sprite_renderer_hardware import rotated_collision


class TestRotatedCollision(unittest.TestCase):
    def setUp(self):
        pass

    def test_rotated_collision(self):
        rect1 = (r(0, 0, 100, 100), 0)
        rect2 = [r(110, 0, 100, 100), 0]

        self.assertFalse(rotated_collision(rect1, rect2))

        rect2[1] = 45
        self.assertTrue(rotated_collision(rect1, rect2))


if __name__ == '__main__':
    unittest.main()
