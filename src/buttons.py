import pygame
#from multi_sprite_renderer_normal import MultiSprite as msr


class Button:
    mousepos = None
    mouse = None
    keyboard = None
    controls = None
    selectedB = None

    debug = True
    debugselectedB = None

    @classmethod
    def input(cls, winscale, mousepos, mouse):
        Button.winscale = winscale
        Button.mousepos = mousepos
        Button.mouse = mouse

    @classmethod
    def select(cls, buttons=None, onlymouse=False):

        if buttons:
            for button in buttons:
                if button.onit and button is not Button.selectedB and (not Button.selectedB or not Button.selectedB.grabbed):
                    Button.selectedB = button
                    break

        if not onlymouse and Button.selectedB and not Button.selectedB.grabbed:
            button = Button.selectedB

            if Button.keyboard[1][Button.controls["Up"]] and not Button.keyboard[0][Button.controls["Up"]] and (s := button.upto):
                Button.selectedB = s

            if Button.keyboard[1][Button.controls["Down"]] and not Button.keyboard[0][Button.controls["Down"]] and (s := button.downto):
                Button.selectedB = s

            if Button.keyboard[1][Button.controls["Left"]] and not Button.keyboard[0][Button.controls["Left"]] and (s := button.leftto):
                Button.selectedB = s

            if Button.keyboard[1][Button.controls["Right"]] and not Button.keyboard[0][Button.controls["Right"]] and (s := button.rightto):
                Button.selectedB = s


    def __init__(self, sprites, name=0, scale=(1, 1), pos=(0, 0), offset=(0, 0), popup=(1, 1), sound=None):
        super().__init__()
        self.sprites = sprites
        self.name = name
        self.scale = scale
        self.pos = pos
        self.offset = offset
        self.popup = popup
        self.xm = self.scale[0]
        self.ym = self.scale[1]
        self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, offset=self.offset)
        self.sound = sound
        self.on = (False, False)
        self.chek = False
        self.checkgrab = False
        self.upto = None
        self.downto = None
        self.leftto = None
        self.rightto = None

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

    def update(self, mode=None) -> tuple:
        match mode:
            case 'draw':
                return self.draw()
            case 'check':
                return self.loop(False)

        return self.loop()

    def linkto(self, up=0, down=0, left=0, right=0):
        if up != 0:
            self.upto = up
        if down != 0:
            self.downto = down
        if left != 0:
            self.leftto = left
        if right != 0:
            self.rightto = right

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

        self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, relativeOffset=self.offset)

        self.on = (self.on[1], pygame.Rect.collidepoint(self.rects[2], mousepos[1]))

        #if (self.on[1] or self is Button.selectedB) and self is not Button.debugselectedB:
        if self is Button.selectedB and self is not Button.debugselectedB:
            self.xm = self.scale[0] * self.popup[0]
            self.ym = self.scale[1] * self.popup[1]
        else:
            self.xm = self.scale[0]
            self.ym = self.scale[1]
        self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, relativeOffset=self.offset)

        if (self is Button.selectedB and mouse[1][0] and not mouse[0][0] and self.on[1]) or (self is Button.selectedB and Button.keyboard[1][Button.controls["Ok"]] and not Button.keyboard[0][Button.controls["Ok"]]):
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

        if Button.debug and self.onnow and Button.keyboard[1][pygame.K_p] and not Button.keyboard[0][pygame.K_p]:
            if self is Button.debugselectedB:
                Button.debugselectedB = None
            else:
                Button.debugselectedB = self

        if Button.debug and self is Button.debugselectedB:
            self.clicked = False
            if self.grabbed:
                self.pos = tuple(mousepos[1])

            if Button.keyboard[1][pygame.K_l] and not Button.keyboard[0][pygame.K_l]:
                self.scale = (self.scale[0] + 0.05, self.scale[1])
            if Button.keyboard[1][pygame.K_j] and not Button.keyboard[0][pygame.K_j]:
                self.scale = (self.scale[0] - 0.05, self.scale[1])
            if Button.keyboard[1][pygame.K_i] and not Button.keyboard[0][pygame.K_i]:
                self.scale = (self.scale[0], self.scale[1] + 0.05)
            if Button.keyboard[1][pygame.K_k] and not Button.keyboard[0][pygame.K_k]:
                self.scale = (self.scale[0], self.scale[1] - 0.05)
            self.scale = (round(self.scale[0], 2), round(self.scale[1], 2))

            if Button.keyboard[1][pygame.K_KP7]:
                self.offset = (-0.5, -0.5)
            if Button.keyboard[1][pygame.K_KP8]:
                self.offset = (0, -0.5)
            if Button.keyboard[1][pygame.K_KP9]:
                self.offset = (0.5, -0.5)
            if Button.keyboard[1][pygame.K_KP4]:
                self.offset = (-0.5, 0)
            if Button.keyboard[1][pygame.K_KP5]:
                self.offset = (0, 0)
            if Button.keyboard[1][pygame.K_KP6]:
                self.offset = (0.5, 0)
            if Button.keyboard[1][pygame.K_KP1]:
                self.offset = (-0.5, 0.5)
            if Button.keyboard[1][pygame.K_KP2]:
                self.offset = (0, 0.5)
            if Button.keyboard[1][pygame.K_KP3]:
                self.offset = (0.5, 0.5)

            if Button.keyboard[1][pygame.K_o] and not Button.keyboard[0][pygame.K_o]:
                print(self.pos, self.scale, self.offset)

        return self.rects

    def draw(self, rects=1):
        if rects:
            self.rects = self.sprites.rects(name=self.name, scale=(self.xm, self.ym), pos=self.pos, relativeOffset=self.offset)
        self.sprites.draw_only(name=self.name, rects=self.rects, scale=(self.xm, self.ym), alpha=0.5 if Button.debug and self is Button.debugselectedB else 1)

        return self.rects


class Slider(Button):
    @staticmethod
    def map_value(value, valuemin, valuemax, mapmin, mapmax):
        return ((value - valuemin) / (valuemax - valuemin)) * (mapmax - mapmin) + mapmin

    def __init__(self, sprites, name=0, scale=(1, 1), pos=(0, 0), offset=(0, 0), popup=(1, 1), sound=None, horizontal=True, posmap=(100, 300), valuemap=(0, 100), stepsize=1):
        super().__init__(sprites, name=name, scale=scale, pos=pygame.Vector2(pos), offset=offset, popup=popup, sound=sound)
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

        if self is Button.selectedB:
            if not self.horizontal and Button.keyboard[1][Button.controls["Up"]] and not Button.keyboard[0][Button.controls["Up"]]:
                self.value += self.stepsize

            if not self.horizontal and Button.keyboard[1][Button.controls["Down"]] and not Button.keyboard[0][Button.controls["Down"]]:
                self.value -= self.stepsize

            if self.horizontal and Button.keyboard[1][Button.controls["Left"]] and not Button.keyboard[0][Button.controls["Left"]]:
                self.value -= self.stepsize

            if self.horizontal and Button.keyboard[1][Button.controls["Right"]] and not Button.keyboard[0][Button.controls["Right"]]:
                self.value += self.stepsize

        if self.grabbed and not self.clicked:
            self.value = ((mousepos[1][not self.horizontal] - self.posmap[0]) / (self.posmap[1] - self.posmap[0])) * (self.valuemap[1] - self.valuemap[0]) + self.valuemap[0]

        return rects

