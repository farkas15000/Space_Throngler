import math
import pygame
from os.path import join
from pygame._sdl2.video import Texture, Renderer


def rotated_collision(rect1: (pygame.Rect, float), rect2: (pygame.Rect, float)):
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
    screen = None
    screenRect = None
    rect = pygame.Rect()
    absRect = pygame.Rect()

    @classmethod
    def setScreen(cls, screen: Renderer | Texture):
        cls.screen = screen
        try:
            cls.screenRect = screen.get_viewport()
        except AttributeError:
            cls.screenRect = screen.get_rect()
        cls.screenRect.x, cls.screenRect.y = 0, 0

    @classmethod
    def flip(cls):
        cls.screen.present()

    def __call__(self, folders=(), names=(), images=(), font=None, size=50, bold=False, italic=False, color='White', background=None, AA=False):
        self.__init__(folders=folders, names=names, images=images, font=font, size=size, bold=bold, italic=italic, color=color, background=background, AA=AA)

    def __init__(self, folders=(), names=(), images=(), font=None, size=50, bold=False, italic=False, color='White', background=None, AA=False):

        self.sprites = {}

        for k, name in enumerate(names):
            img = pygame.image.load(join(*folders, name + '.png'))
            texture = Texture.from_surface(MultiSprite.screen, img)
            texture.blend_mode = pygame.BLENDMODE_BLEND
            rect = texture.get_rect()

            self.sprites[k] = (texture, rect)

        num = len(self.sprites)

        for k, img in enumerate(images):
            texture = Texture.from_surface(MultiSprite.screen, img)
            texture.blend_mode = pygame.BLENDMODE_BLEND
            rect = texture.get_rect()

            self.sprites[k+num] = (texture, rect)

        if not names and not images and font:
            self.size = size
            self.bold = bold
            self.italic = italic
            self.color = color
            self.background = background
            self.AA = AA
            self.font = pygame.font.Font(join(*folders, font + '.ttf'), size)
            self.font.set_bold(bold)
            self.font.set_italic(italic)

            for char in ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\n':
                img = self.font.render(char, AA, color, background)
                texture = Texture.from_surface(MultiSprite.screen, img)
                texture.blend_mode = pygame.BLENDMODE_BLEND
                rect = texture.get_rect()

                self.sprites[char] = (texture, rect)

    def draw(self, name: int | str = 0, scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), offset=(0, 0), rotation=0, flip=(0, 0), alpha=1):

        rect = MultiSprite.rect
        rect.size = self.sprites[name][1].size
        rect.scale_by_ip(*scale)
        size = pygame.Vector2(rect.size)
        top_left = -pygame.Vector2(size.x * relativeOffset[0] + offset[0], size.y * relativeOffset[1] + offset[1]).rotate(-rotation) + size // -2 + pos
        rect.topleft = math.floor(top_left.x + 0.00001), math.floor(top_left.y + 0.00001)

        r = abs((rotation+90) % 180-90)
        area = pygame.Vector2(rect.size)
        abs_rect = MultiSprite.absRect
        abs_rect.size = area.rotate(-r).x, area.rotate(r).y
        abs_rect.center = rect.center

        if rendered := MultiSprite.screenRect.colliderect(abs_rect) and alpha > 0:
            self.sprites[name][0].alpha = 255*alpha
            self.sprites[name][0].draw(dstrect=rect, angle=-rotation, origin=None, flip_x=flip[0], flip_y=flip[1])

        return rect, rotation, abs_rect, rendered

    def rects(self, name: int | str = 0, scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), offset=(0, 0), rotation=0, **kwargs):

        rect = pygame.Rect()
        rect.size = self.sprites[name][1].size
        rect.scale_by_ip(*scale)
        size = pygame.Vector2(rect.size)
        top_left = -pygame.Vector2(size.x * relativeOffset[0] + offset[0], size.y * relativeOffset[1] + offset[1]).rotate(-rotation) + size // -2 + pos
        rect.topleft = math.floor(top_left.x + 0.00001), math.floor(top_left.y + 0.00001)

        r = abs((rotation + 90) % 180 - 90)
        area = pygame.Vector2(rect.size)
        abs_rect = pygame.Rect()
        abs_rect.size = area.rotate(-r).x, area.rotate(r).y
        abs_rect.center = rect.center

        return rect, rotation, abs_rect, MultiSprite.screenRect.colliderect(abs_rect)

    def draw_only(self, name: int | str = 0, rects=None, flip=(0, 0), alpha=1, **kwargs):

        if rendered := MultiSprite.screenRect.colliderect(rects[2]) and alpha > 0:
            self.sprites[name][0].alpha = 255 * alpha
            self.sprites[name][0].draw(dstrect=rects[0], angle=-rects[1], origin=None, flip_x=flip[0], flip_y=flip[1])

        return rendered

    def add_char(self, char):
        img = self.font.render(char, self.AA, self.color, self.background)
        texture = Texture.from_surface(MultiSprite.screen, img)
        rect = texture.get_rect()

        self.sprites[char] = (texture, rect)

    def write(self, text='', scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), align=1, rotation=0, flip=(0, 0), alpha=1):

        width = 0
        enter = 0
        lines = text.split('\n')
        y = relativeOffset[1] * len(lines) + (len(lines) - 1) * 0.5

        line_widths = list(0 for _ in range(len(lines)))
        for k, line in enumerate(lines):
            for char in line:
                try:
                    line_widths[k] += int(self.sprites[char][1].w * scale[0])
                except KeyError:
                    self.add_char(char)
                    line_widths[k] += int(self.sprites[char][1].w * scale[0])
        widest = max(line_widths)

        if align == 1:  # left
            pos = (pos[0] + (widest * (-relativeOffset[0] - 0.5)), pos[1])
        elif align == -1:  # right
            pos = (pos[0] + (widest * (-relativeOffset[0] + 0.5)), pos[1])
        elif align == 0:  # center
            pos = (pos[0] + (widest * (-relativeOffset[0])), pos[1])

        for lk, line in enumerate(lines):
            for k, char in enumerate(line):
                if align == 1:  # left
                    w = int(self.sprites[line[k]][1].w * scale[0])
                    self.draw(name=line[k], scale=scale, pos=pos,
                              relativeOffset=(width / w - 0.5, y - enter / self.sprites[line[k]][1].h),
                              rotation=rotation, flip=flip, alpha=alpha)
                    width -= w

                elif align == -1:  # right
                    w = int(self.sprites[line[-k - 1]][1].w * scale[0])
                    self.draw(name=line[-k - 1], scale=scale, pos=pos,
                              relativeOffset=(width / w + 0.5, y - enter / self.sprites[line[-k - 1]][1].h),
                              rotation=rotation, flip=flip, alpha=alpha)
                    width += w

                elif align == 0:  # center
                    w = int(self.sprites[line[k]][1].w * scale[0])
                    self.draw(name=line[k], scale=scale, pos=pos,
                              relativeOffset=(width / w - 0.5, y - enter / self.sprites[line[k]][1].h),
                              offset=(line_widths[lk] * 0.5, 0), rotation=rotation, flip=flip, alpha=alpha)
                    width -= w

            width = 0
            enter += self.sprites['A'][1].h

        return line_widths
