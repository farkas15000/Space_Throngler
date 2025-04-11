import pygame
from multi_sprite_renderer_hardware import MultiSprite as Msr


class Particle(pygame.sprite.Sprite):
    dt = None

    def __init__(
        self,
        pos,
        sprites: Msr,
        animation,
        velocity,
        scale=None,
        relativeOffset=None,
        rotation=0,
        turn=0,
    ):
        """
        animation: List where first element is the lifetime of the particle,
        others are sprite index numbers
        velocity: moving direction, turn: turning speed
        """

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
        self._duration = self.animation[0] / (len(self.animation) - 1)
        self.animTimer = 0
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.rotation = rotation
        self.turn = turn
        self.flipX = False
        self.flipy = False
        self.rect = pygame.rect.Rect(1, 1, 1, 1)

    def update(self, mode=None):
        match mode:
            case "draw":
                self.draw()
            case "loop":
                self.loop()
            case _:
                self.loop()
                self.draw()

    def draw(self):
        rects = self.msr.rects(
            self.frame,
            pos=self.pos,
            scale=self.scale,
            relativeOffset=self.relativeOffset,
            rotation=self.rotation,
        )
        self.rect = rects[2]
        self.msr.draw_only(self.frame, rects, flip=(self.flipX, self.flipy))

        if not self.rect[3]:
            self.kill()

    def animator(self):
        length = len(self.animation) - 1
        full = self.animation[0]
        duration = full / length
        self.frame = self.animation[
            int((self.animTimer // duration) % length + 1)
        ]
        self.animTimer += Particle.dt
        if self.animTimer >= full:
            self.animTimer %= full
            return True
        return False

    def move(self):
        self.pos += self.velocity * Particle.dt
        self.rotation += self.turn * Particle.dt

    def loop(self):

        if self.animator():
            self.kill()

        self.move()
