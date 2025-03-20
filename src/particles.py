import pygame
from multi_sprite_renderer_hardware import MultiSprite as msr

class Particle(pygame.sprite.Sprite):
    dt = None  # has to be set every frame!
    sprites = None  # can hold a main msr containing all sprites to be used

    def __init__(self, pos, sprites: msr, animation, velocity, scale=None, relativeOffset=None, rotation=0, turn=0):
        # animation = List where first element is the lifetime of the particle, others are sprite index numbers
        # velocity = moving direction, turn = turning speed

        super().__init__()
        self.msr = sprites
        if scale is None:
            self.scale = [1, 1]
        else:
            self.scale = scale
        if relativeOffset is None:
            self.relativeOffset = [0, 0]
        else:
            self.relativeOffset = relativeOffset
        self.frame = 0
        self.animation = animation
        self._length = 1 / (len(self.animation) - 1)
        self._durat = self.animation[0] / (len(self.animation) - 1)
        self.animtimer = 0
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.rotation = rotation
        self.turn = turn
        self.flipx = False
        self.flipy = False
        self.rect = pygame.rect.Rect(1, 1, 1, 1)

    def update(self, mode=None):
        match mode:
            case 'draw':
                self.draw()
            case 'loop':
                self.loop()
            case _:
                self.loop()
                self.draw()

    def draw(self):
        self.rect = self.msr.draw(self.frame, pos=self.pos, scale=self.scale,
                                  offset=self.relativeOffset, rotation=self.rotation, flip=(self.flipx, self.flipy))[2]
        if not self.rect[3]:
            self.kill()

    def animator(self):
        length = len(self.animation) - 1
        full = self.animation[0]
        durat = full / length
        self.frame = self.animation[int((self.animtimer // durat)%length + 1)]
        self.animtimer += Particle.dt
        if self.animtimer >= full:
            self.animtimer %= full
            return True
        return False

    def move(self):
        self.pos += self.velocity * Particle.dt
        self.rotation += self.turn * Particle.dt

    def loop(self):

        if self.animator():
            self.kill()

        self.move()
