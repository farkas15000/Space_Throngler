import unittest
import pygame
import entity


class TestEntityUtils(unittest.TestCase):
    def setUp(self):
        pass

    def test_dotsRot(self):
        vec1 = pygame.Vector2(10, 0)
        vec2 = pygame.Vector2(10, -10)
        self.assertEqual(90, entity.dotsRot(vec1, vec2))

        vec1 = pygame.Vector2(0, 0)
        vec2 = pygame.Vector2(12, -12)
        self.assertEqual(45, entity.dotsRot(vec1, vec2))

    def test_map_value(self):
        self.assertEqual(50, entity.map_value(20, 0, 40, 0, 100))

        self.assertEqual(12, entity.map_value(60, 0, 50, 0, 10))


if __name__ == '__main__':
    unittest.main()
