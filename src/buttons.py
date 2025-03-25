import pygame
from multi_sprite_renderer_hardware import MultiSprite as Msr


class Button(pygame.sprite.Sprite):
    mousepos = None
    mouse = None
    keyword = None

    @classmethod
    def input(cls, mousepos, mouse, keyboard):
        Button.mousepos = mousepos
        Button.mouse = mouse
        Button.keyboard = keyboard

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
        self.chek = False
        self.checkgrab = False

        # button test results ment to be used
        self.clicked = 0
        self.held = 0
        self.released = 0
        self.grabbed = 0
        self.grab_released = 0
        self.sticked = 0
        self.onit = 0
        self.offit = 0
        self.onnow = 0

    def update(self, mode=None):
        match mode:
            case 'draw':
                self.draw()
            case 'check':
                self.loop(False)
            case _:
                self.loop()

    def loop(self, draw=True, sound=True, mousepos=None, mouse=None, ungrab=False, unstick=False):
        # update button tests

        if mousepos is None:
            mousepos = Button.mousepos
        if mouse is None:
            mouse = Button.mouse
        self.clicked = 0
        self.held = 0
        self.released = 0
        self.grab_released = 0
        self.onit = 0
        self.offit = 0
        self.onnow = 0

        self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, relativeOffset=self.relativeOffset)

        self.on = (self.on[1], pygame.Rect.collidepoint(self.rects[2], mousepos[1]))
        if self.on[1]:
            self.xm = self.scale[0] * self.popup[0]
            self.ym = self.scale[1] * self.popup[1]
        else:
            self.xm = self.scale[0]
            self.ym = self.scale[1]
        self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, relativeOffset=self.relativeOffset)

        if mouse[1][0] and not mouse[0][0] and self.on[1]:
            self.chek = True
            self.clicked = 1

        if mouse[1][0] and self.on[1] and (self.checkgrab or self.clicked):
            self.checkgrab = True
            self.held = 1
        else:
            self.checkgrab = False

        grabbed = self.grabbed

        if (self.clicked or (self.grabbed and mouse[1][0])) and not ungrab:
            self.grabbed = 1
        else:
            self.grabbed = 0

        if not self.grabbed and grabbed:
            self.grab_released = 1

        if not mouse[1][0] and mouse[0][0] and self.chek and self.on[0] or (self.chek and not self.on[0]):
            self.chek = False
            self.released = 1

        if self.on[1] and not self.on[0]:
            self.onit = 1

        elif not self.on[1] and self.on[0]:
            self.offit = 1

        if self.on[1]:
            self.onnow = 1

        if mouse[1][0]:
            if self.onnow or self.sticked:
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
    def map_value(value, valuemin, valuemax, mapmin, mapmax):
        return ((value - valuemin) / (valuemax - valuemin)) * (mapmax - mapmin) + mapmin

    def __init__(self, sprites, name=0, scale=(1, 1), pos=(0, 0), relativeOffset=(0, 0), popup=(1, 1), sound=None, horizontal=True, posmap=(100, 300), valuemap=(0, 100), stepsize=1):
        super().__init__(sprites, name=name, scale=scale, pos=pygame.Vector2(pos), relativeOffset=relativeOffset, popup=popup, sound=sound)
        self.posmap = posmap
        self.valuemap = valuemap
        self.stepsize = stepsize
        self.horizontal = horizontal
        self.value = valuemap[0]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        mod = value % self.stepsize
        value = int(pygame.math.clamp(value - mod + (self.stepsize if mod*2 >= self.stepsize else 0), self.valuemap[0], self.valuemap[1]))

        self._value = value
        self.pos[not self.horizontal] = ((value - self.valuemap[0]) / (self.valuemap[1] - self.valuemap[0])) * (self.posmap[1] - self.posmap[0]) + self.posmap[0]

    def loop(self, draw=True, sound=True, mousepos=None, mouse=None, ungrab=False, unstick=False):
        rects = super().loop(draw, sound, mousepos, mouse, ungrab, unstick)

        if mousepos is None:
            mousepos = Button.mousepos

        if self.grabbed and not self.clicked:
            self.value = ((mousepos[1][not self.horizontal] - self.posmap[0]) / (self.posmap[1] - self.posmap[0])) * (self.valuemap[1] - self.valuemap[0]) + self.valuemap[0]

        return rects
