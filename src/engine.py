import pygame
from multi_sprite_renderer_hardware import MultiSprite as Msr


class StateMachine:
    states = dict()
    loadins = []
    state = None
    prevstate = None
    app = None

    @classmethod
    def loadin(cls):
        for load in cls.loadins:
            load()


class Camera:
    def __init__(self):
        self.shake = pygame.Vector2(0, 0)
        self.shaketimer = 0
        self.layers = dict()
        self.sorts = dict()
        self.pos = pygame.Vector2(0, 0)
        self.zoom = 1
        self.rect = pygame.Rect()

    def draw_layer(self, key):
        if key in self.sorts.keys():
            self.layers[key].sort(key=self.sorts[key])
        for sprite in self.layers[key]:
            sprite.draw()

    def draw_all(self):
        keys = list(self.layers.keys())
        keys.sort()
        for key in keys:
            self.draw_layer(key)

    def link_camera(self):
        for key in self.layers.keys():
            for sprite in self.layers[key]:
                sprite.camera = self

    def delink_camera(self):
        for key in self.layers.keys():
            for sprite in self.layers[key]:
                del sprite.camera
            self.layers[key] = None
        self.layers.clear()

    def __del__(self):
        #print("deleted: Camera")
        pass


class Sprite:
    def __init__(self, msr: Msr, i):
        self.msr = msr
        self.i = i

    def draw(self):
        self.msr.draw()
