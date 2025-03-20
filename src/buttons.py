import pygame
from multi_sprite_renderer_hardware import MultiSprite as Msr


class Button(pygame.sprite.Sprite):
    winscale = None
    mousepos = None
    mouse = None

    @classmethod
    def input(cls, winscale, mousepos, mouse):
        Button.mousepos = mousepos
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

