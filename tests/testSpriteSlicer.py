import unittest
import pygame
from src import assets


class TestAssets(unittest.TestCase):
    def setUp(self):
        pass

    def test_sprite_slicer(self):
        surf = pygame.Surface((100, 100))
        slices = assets.sprite_slicer(30, 50, surface=surf)
        self.assertEqual(6, len(slices))
        self.assertEqual((30, 50), slices[0].size)


if __name__ == '__main__':
    unittest.main()
