'''
This is the non _sdl2 variant with caching.
'''

import pygame
from os.path import join


def rotated_collision(rect1, rect2):
    # input 2 rects with a rotations: [Rect, rot]
    # draw or rests first 2 return elements can be used with another

    rect1 = (pygame.Vector2(rect1[0].center), pygame.Vector2(rect1[0].topleft) - rect1[0].center), rect1[1]
    rect2 = (pygame.Vector2(rect2[0].center), pygame.Vector2(rect2[0].topleft) - rect2[0].center), rect2[1]
    rec = (rect1, rect2)
    for x in (0, 1):
        center = (rec[1-x][0][0]-rec[0-x][0][0]).rotate(rec[0-x][1])
        r = abs((rec[0-x][1] - rec[1-x][1] + 90) % 180 - 90)
        edges = (abs((rec[1-x][0][1].rotate(r)).elementwise()),
                 abs((rec[1-x][0][1].rotate(-r)).elementwise()))

        for y in (0, 1):
            if not ((-edges[1 - y][y] <= rec[0-x][0][1][y]-center[y] <= edges[1 - y][y]) or
                    (rec[0-x][0][1][y] <= -edges[1 - y][y]+center[y] <= -rec[0-x][0][1][y])):
                return False
    return True


class MultiSprite:
    toblit = []
    offset = pygame.Vector2()

    @classmethod
    def flip(cls, renderer: pygame.surface.Surface):
        # has to be in main loop before pygame.display.update() !
        # will draw above any non MSR draws

        if cls.toblit:
            renderer.fblits(cls.toblit)
            cls.toblit.clear()

    def __init__(self, renderer, folders=(), names=(), images=(), alpha=1, font=None, size=50, bold=False, italic=False, color='White', background=None, AA=False):
        # renderer Surface
        # file names come before images in indexing
        # don't mix names and images with font
        # alpha pre-set, can be modified to be cached

        self.sprites = {}
        self.renderer = renderer
        self.windowrect = self.renderer.get_rect()
        self.windowrect.x, self.windowrect.y = 0, 0

        for k, name in enumerate(names):
            img = pygame.image.load(join(*folders, name + '.png')).convert_alpha()
            img.set_alpha(255*alpha)
            rect = img.get_rect()

            self.sprites[k] = (img, rect)

        num = len(self.sprites)

        for k, img in enumerate(images):
            img = img.convert_alpha()
            img.set_alpha(255 * alpha)
            rect = img.get_rect()

            self.sprites[k+num] = (img, rect)

        if not names and not images:
            self.size = size
            self.bold = bold
            self.italic = italic
            self.color = color
            self.background = background
            self.AA = AA
            self.font = pygame.font.Font(join(*folders, font + '.ttf'), size)
            self.font.set_bold(bold)
            self.font.set_italic(italic)

            for char in ' !"#$%& \'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~\n':
                img = self.font.render(char, AA, color, background).convert_alpha()
                img.set_alpha(255 * alpha)
                rect = img.get_rect()

                self.sprites[char] = (img, rect)

    def draw(self, name=0, scale=(1, 1), pos=(0, 0), offset=(-0.5, -0.5), rotation=0, flip=(0, 0)):
        # name = sprite index in order, scale relative, pos = origin point
        # offset relative shift from pos works with rotation, (-0.5, -0.5)=topleft, (0, 0)=center
        # returns: rect of drawn sprite with rotation, fully encapsulating rect, if it was drawn

        rotation = round(rotation - (rotation % 3)) % 360
        scale = round(scale[0], 2), round(scale[1], 2)

        rect: pygame.rect.Rect = self.sprites[name][1].copy()
        size = pygame.Vector2(rect.w*scale[0], rect.h*scale[1])
        rect.scale_by_ip(*scale)
        rect.topleft = -pygame.Vector2(size[0] * offset[0], size[1] * offset[1]).rotate(-rotation) + size/-2 + pos + MultiSprite.offset

        r = abs((rotation+90)%180-90)
        edge1 = ((pygame.Vector2(rect.topleft) - rect.center).rotate(-r))
        edge2 = ((pygame.Vector2(rect.topleft) - rect.center).rotate(r))

        absrect = rect.copy()
        absrect.w = edge1.x*2
        absrect.h = edge2.y*2
        absrect.normalize()
        absrect.center = rect.center

        if rendered := self.windowrect.colliderect(absrect):

            try:
                MultiSprite.toblit.append((self.sprites[(name, *scale, rotation, *flip)], absrect.topleft))
            except KeyError:
                img = self.sprites[name][0].copy()
                img = pygame.transform.flip(img, *flip)
                img = pygame.transform.scale(img, (rect.w, rect.h))
                img = pygame.transform.rotate(img, rotation)

                self.sprites[(name, *scale, rotation, *flip)] = img
                MultiSprite.toblit.append((img, absrect.topleft))

        '''pygame.draw.rect(self.renderer, (255, 0, 255, 0), (pos, (5, 5)), width=1)
        pygame.draw.rect(self.renderer, (0, 0, 255, 0), absrect, width=1)
        pygame.draw.rect(self.renderer, (0, 255, 0, 0), rect, width=1)'''

        return rect, rotation, absrect, rendered

    def rects(self, name=0, scale=(1, 1), pos=(0, 0), offset=(-0.5, -0.5), rotation=0, **kwargs):
        # returns: rect of drawn sprite with rotation, fully encapsulating rect, if it would be drawn

        rotation = round(rotation - (rotation % 3)) % 360
        scale = round(scale[0], 2), round(scale[1], 2)

        rect = self.sprites[name][1].copy()
        size = pygame.Vector2(rect.w * scale[0], rect.h * scale[1])
        rect.scale_by_ip(*scale)
        rect.topleft = -pygame.Vector2(size[0] * offset[0], size[1] * offset[1]).rotate(-rotation) + size/-2 + pos + MultiSprite.offset

        r = abs((rotation+90)%180-90)

        edge1 = ((pygame.Vector2(rect.topleft) - rect.center).rotate(-r))
        edge2 = ((pygame.Vector2(rect.topleft) - rect.center).rotate(r))

        absrect = rect.copy()
        absrect.w = edge1.x * 2
        absrect.h = edge2.y * 2
        absrect.normalize()
        absrect.center = rect.center

        return rect, rotation, absrect, self.windowrect.colliderect(absrect)

    def draw_only(self, name, rects, scale, flip=(0, 0)):
        # needs rects from draw or rects also the scale that was used there
        # returns: if it was rendered

        scale = round(scale[0], 2), round(scale[1], 2)

        if rendered := self.windowrect.colliderect(rects[2]):

            try:
                MultiSprite.toblit.append((self.sprites[(name, *scale, rects[1], *flip)], rects[2].topleft))
            except KeyError:
                img = self.sprites[name][0].copy()
                img = pygame.transform.flip(img, *flip)
                img = pygame.transform.scale(img, (rects[0].w, rects[0].h))
                img = pygame.transform.rotate(img, rects[1])

                self.sprites[(name, *scale, rects[1], *flip)] = img
                MultiSprite.toblit.append((img, rects[2].topleft))

        return rendered

    def add_char(self, char):
        # automatic, don't use
        img = self.font.render(char, self.AA, self.color, self.background)
        rect = img.get_rect()

        self.sprites[char] = (img, rect)

    def write(self, text='', scale=(1, 1), pos=(0, 0), offset=(False, 0), rotation=0, flip=(0, 0)):
        # scaled from original given font size. pos = origin point
        # offset[0]=bool write from left to right or backwards, offset[1]=relative vertical offset given from whole text height
        # rotation rotates whole text, flip applied to characters

        width = 0
        enter = 0
        lines = text.split('\n')
        y = offset[1]*len(lines)-0.5

        for line in lines:
            for k, char in enumerate(line):
                if offset[0]:
                    try:
                        self.draw(name=line[-k-1], scale=scale, pos=pos, offset=(width/self.sprites[line[-k-1]][1].w+0.5, y-enter/self.sprites[line[-k-1]][1].h), rotation=rotation, flip=flip)
                    except KeyError:
                        self.add_char(line[-k-1])
                        self.draw(name=line[-k-1], scale=scale, pos=pos, offset=(width/self.sprites[line[-k-1]][1].w+0.5, y-enter/self.sprites[line[-k-1]][1].h), rotation=rotation, flip=flip)
                    width += self.sprites[line[-k-1]][1].w
                else:
                    try:
                        self.draw(name=line[k], scale=scale, pos=pos, offset=(width/self.sprites[line[k]][1].w-0.5, y-enter/self.sprites[line[k]][1].h), rotation=rotation, flip=flip)
                    except KeyError:
                        self.add_char(line[k])
                        self.draw(name=line[k], scale=scale, pos=pos, offset=(width/self.sprites[line[k]][1].w-0.5, y-enter/self.sprites[line[k]][1].h), rotation=rotation, flip=flip)
                    width -= self.sprites[line[k]][1].w
            width = 0
            enter += self.sprites['A'][1].h

    def __len__(self):
        return len(self.sprites)
