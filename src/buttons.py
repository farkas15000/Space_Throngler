import pygame
from multi_sprite_renderer_hardware import MultiSprite as Msr


class Button(pygame.sprite.Sprite):
    mousePos = None
    mouse = None

    @classmethod
    def input(cls, mouse_pos, mouse):
        Button.mousePos = mouse_pos
        Button.mouse = mouse

    def __init__(self, sprites: Msr, name=0, scale=(1, 1), pos=(0, 0), relativeOffset=(0, 0), popup=(1, 1), sound=None):
        super().__init__()
        self.sprites = sprites
        self.name = name
        self.scale = scale
        self.pos = pos
        self.relativeOffset = relativeOffset
        self.popup = popup
        self.xm = self.scale[0]
        self.ym = self.scale[1]
        self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, relativeOffset=self.relativeOffset)
        self.sound = sound
        self.on = (False, False)
        self.check = False
        self.checkGrab = False

        # button test results ment to be used
        self.clicked = 0
        self.held = 0
        self.released = 0
        self.grabbed = 0
        self.grab_released = 0
        self.sticked = 0
        self.onIt = 0
        self.offIt = 0
        self.onNow = 0

    def update(self, mode=None):
        match mode:
            case 'draw':
                self.draw()
            case 'check':
                self.loop(False)
            case _:
                self.loop()

    def loop(self, draw=True, sound=True, mouse_pos=None, mouse=None, ungrab=False, unstick=False):
        """checks button interactions"""

        if mouse_pos is None:
            mouse_pos = Button.mousePos
        if mouse is None:
            mouse = Button.mouse
        self.clicked = 0
        self.held = 0
        self.released = 0
        self.grab_released = 0
        self.onIt = 0
        self.offIt = 0
        self.onNow = 0

        self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, relativeOffset=self.relativeOffset)

        self.on = (self.on[1], pygame.Rect.collidepoint(self.rects[2], mouse_pos[1]))
        if self.on[1]:
            self.xm = self.scale[0] * self.popup[0]
            self.ym = self.scale[1] * self.popup[1]
        else:
            self.xm = self.scale[0]
            self.ym = self.scale[1]
        self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, relativeOffset=self.relativeOffset)

        if mouse[1][0] and not mouse[0][0] and self.on[1]:
            self.check = True
            self.clicked = 1

        if mouse[1][0] and self.on[1] and (self.checkGrab or self.clicked):
            self.checkGrab = True
            self.held = 1
        else:
            self.checkGrab = False

        grabbed = self.grabbed

        if (self.clicked or (self.grabbed and mouse[1][0])) and not ungrab:
            self.grabbed = 1
        else:
            self.grabbed = 0

        if not self.grabbed and grabbed:
            self.grab_released = 1

        if not mouse[1][0] and mouse[0][0] and self.check and self.on[0] or (self.check and not self.on[0]):
            self.check = False
            self.released = 1

        if self.on[1] and not self.on[0]:
            self.onIt = 1

        elif not self.on[1] and self.on[0]:
            self.offIt = 1

        if self.on[1]:
            self.onNow = 1

        if mouse[1][0]:
            if self.onNow or self.sticked:
                self.sticked = 1
        else:
            self.sticked = 0
        self.sticked = self.sticked and not unstick

        if draw:
            self.draw(0)

        if self.clicked and sound and self.sound:
            self.sound.play()

    def draw(self, rects=1):
        if rects:
            self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, relativeOffset=self.relativeOffset)
        self.sprites.draw_only(name=self.name, rects=self.rects, scale=(self.xm, self.ym))


class Slider(Button):
    @staticmethod
    def map_value(value, value_min, value_max, map_min, map_max):
        return ((value - value_min) / (value_max - value_min)) * (map_max - map_min) + map_min

    def __init__(self, sprites, name=0, scale=(1, 1), pos=(0, 0), relativeOffset=(0, 0), popup=(1, 1), sound=None, horizontal=True, pos_map=(100, 300), value_map=(0, 100), step_size=1):
        super().__init__(sprites, name=name, scale=scale, pos=pygame.Vector2(pos), relativeOffset=relativeOffset, popup=popup, sound=sound)
        self.posMap = pos_map
        self.valueMap = value_map
        self.stepSize = step_size
        self.horizontal = horizontal
        self.value = value_map[0]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        mod = value % self.stepSize
        value = int(pygame.math.clamp(value - mod + (self.stepSize if mod * 2 >= self.stepSize else 0), self.valueMap[0], self.valueMap[1]))

        self._value = value
        self.pos[not self.horizontal] = ((value - self.valueMap[0]) / (self.valueMap[1] - self.valueMap[0])) * (self.posMap[1] - self.posMap[0]) + self.posMap[0]

    def loop(self, draw=True, sound=True, mouse_pos=None, mouse=None, ungrab=False, unstick=False):
        rects = super().loop(draw, sound, mouse_pos, mouse, ungrab, unstick)

        if mouse_pos is None:
            mouse_pos = Button.mousePos

        if self.grabbed and not self.clicked:
            self.value = ((mouse_pos[1][not self.horizontal] - self.posMap[0]) / (self.posMap[1] - self.posMap[0])) * (self.valueMap[1] - self.valueMap[0]) + self.valueMap[0]

        return rects
