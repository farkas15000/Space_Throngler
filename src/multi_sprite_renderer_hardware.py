'''
This is the _sdl2 variant.
'''

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
    screenrect = None
    rect = pygame.Rect()
    absrect = pygame.Rect()

    @classmethod
    def setScreen(cls, screen: Renderer):
        cls.screen = screen
        try:
            cls.screenrect = screen.get_viewport()
        except AttributeError:
            cls.screenrect = screen.get_rect()
        cls.screenrect.x, cls.screenrect.y = 0, 0

    @classmethod
    def flip(cls):
        cls.screen.present()

    def __call__(self, folders=(), names=(), images=(), font=None, size=50, bold=False, italic=False, color='White', background=None, AA=False):
        self.__init__(folders=folders, names=names, images=images, font=font, size=size, bold=bold, italic=italic, color=color, background=background, AA=AA)

    def __init__(self, folders=(), names=(), images=(), font=None, size=50, bold=False, italic=False, color='White', background=None, AA=False):
        # renderer Surface
        # file names come before images in indexing
        # don't mix names and images with font
        # alpha pre-set, can be modified to be cached

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

            for char in ' !"#$%& \'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~\n':
                img = self.font.render(char, AA, color, background)
                texture = Texture.from_surface(MultiSprite.screen, img)
                texture.blend_mode = pygame.BLENDMODE_BLEND
                rect = texture.get_rect()

                self.sprites[char] = (texture, rect)

    def draw(self, name=0, scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), offset=(0, 0), rotation=0, flip=(0, 0), alpha=1):
        # name = sprite index in order, scale relative, pos = origin point
        # offset relative shift from pos works with rotation, (-0.5, -0.5)=topleft, (0, 0)=center
        # returns: rect of drawn sprite with rotation, fully encapsulating rect, if it was drawn

        rect = MultiSprite.rect
        rect.size = self.sprites[name][1].size
        rect.scale_by_ip(*scale)
        size = pygame.Vector2(rect.size)
        topleft = -pygame.Vector2(size.x * relativeOffset[0] + offset[0], size.y * relativeOffset[1] + offset[1]).rotate(-rotation) + size // -2 + pos
        rect.topleft = math.floor(topleft.x + 0.00001), math.floor(topleft.y + 0.00001)

        r = abs((rotation+90) % 180-90)
        area = pygame.Vector2(rect.size)
        absrect = MultiSprite.absrect
        absrect.size = area.rotate(-r).x, area.rotate(r).y
        absrect.center = rect.center

        if rendered := MultiSprite.screenrect.colliderect(absrect) and alpha > 0:
            self.sprites[name][0].alpha = 255*alpha
            self.sprites[name][0].draw(dstrect=rect, angle=-rotation, origin=None, flip_x=flip[0], flip_y=flip[1])

        '''self.screen.draw_color = (0, 0, 255, 0)
        self.screen.draw_rect(absrect)
        self.screen.draw_color = (0, 255, 0, 0)
        self.screen.draw_rect(rect)
        self.screen.draw_color = (255, 0, 255, 0)
        self.screen.draw_rect((pos, (2, 2)))
        self.screen.draw_color = (0, 0, 0, 0)'''
        #self.renderer.draw_rect((pygame.Vector2(pos) - (rect.w * offset[0], rect.h * offset[1]) + (rect.w/2, rect.h/2), (5, 5)))
        #self.renderer.draw_rect(((pygame.Vector2(pos) -(pygame.Vector2(pos) - (rect.w * offset[0], rect.h * offset[1]) + (rect.w/2, rect.h/2))).rotate(-rotation)+pygame.Vector2(pos) - (rect.w * offset[0], rect.h * offset[1]) + (rect.w/2, rect.h/2), (5, 5)))
        #print((pygame.Vector2(pos) -(pygame.Vector2(pos) - (rect.w * offset[0], rect.h * offset[1]) + (rect.w/2, rect.h/2))).rotate(-rotation)+pygame.Vector2(pos) - (rect.w * offset[0], rect.h * offset[1]) + (rect.w/2, rect.h/2)-pos)
        #self.renderer.draw_color = (0, 0, 0, 0)

        return rect, rotation, absrect, rendered

    def rects(self, name=0, scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), offset=(0, 0), rotation=0, **kwargs):

        rect = pygame.Rect()  # MultiSprite.rect
        rect.size = self.sprites[name][1].size
        rect.scale_by_ip(*scale)
        size = pygame.Vector2(rect.size)
        topleft = -pygame.Vector2(size.x * relativeOffset[0] + offset[0], size.y * relativeOffset[1] + offset[1]).rotate(-rotation) + size // -2 + pos
        rect.topleft = math.floor(topleft.x + 0.00001), math.floor(topleft.y + 0.00001)

        r = abs((rotation + 90) % 180 - 90)
        area = pygame.Vector2(rect.size)
        absrect = pygame.Rect()  # MultiSprite.absrect
        absrect.size = area.rotate(-r).x, area.rotate(r).y
        absrect.center = rect.center

        return rect, rotation, absrect, MultiSprite.screenrect.colliderect(absrect)

    def draw_only(self, name=0, rects=None, flip=(0, 0), alpha=1, **kwargs):

        if rendered := MultiSprite.screenrect.colliderect(rects[2]) and alpha > 0:
            self.sprites[name][0].alpha = 255 * alpha
            self.sprites[name][0].draw(dstrect=rects[0], angle=-rects[1], origin=None, flip_x=flip[0], flip_y=flip[1])

        return rendered

    def add_char(self, char):
        img = self.font.render(char, self.AA, self.color, self.background)
        texture = Texture.from_surface(MultiSprite.screen, img)
        rect = texture.get_rect()

        self.sprites[char] = (texture, rect)

    def write(self, text='', scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), align=1, rotation=0, flip=(0, 0), alpha=1):
        # scaled from original given font size. pos = origin point
        # rotation rotates whole text, flip applied to characters

        width = 0
        enter = 0
        lines = text.split('\n')
        y = relativeOffset[1] * len(lines) + (len(lines) - 1) * 0.5

        linewidths = list(0 for _ in range(len(lines)))
        for k, line in enumerate(lines):
            for char in line:
                try:
                    linewidths[k] += int(self.sprites[char][1].w * scale[0])
                except KeyError:
                    self.add_char(char)
                    linewidths[k] += int(self.sprites[char][1].w * scale[0])
        widest = max(linewidths)

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
                              offset=(linewidths[lk] * 0.5, 0), rotation=rotation, flip=flip, alpha=alpha)
                    width -= w

            width = 0
            enter += self.sprites['A'][1].h

        return linewidths

    def write_clamped(self, text='', width=1, scale=(1, 1), pos=(0, 0), relativeOffset=(-0.5, -0.5), align=1, rotation=0, flip=(0, 0), alpha=1):
        # scaled from original given font size. pos = origin point
        # rotation rotates whole text, flip applied to characters

        current_line = ""
        current_width = 0
        result = ""
        for char in text:
            try:
                char_w = int(self.sprites[char][1].w * scale[0])
            except KeyError:
                self.add_char(char)
                char_w = int(self.sprites[char][1].w * scale[0])
            # Check if adding this character would exceed the max_width
            if current_width + char_w > width:
                # Find the last space in the current line to break the line
                last_space_index = current_line.rfind(' ')
                if last_space_index != -1:
                    # Break the line at the last space
                    result += current_line[:last_space_index] + '\n'
                    # Start the new line with the remainder after the space
                    current_line = current_line[last_space_index + 1:] + char
                    current_width = sum(int(self.sprites[char][1].w * scale[0]) for c in current_line)
                else:
                    # No spaces, force break the line
                    result += current_line + '\n'
                    if char != ' ':
                        current_line = char
                        current_width = char_w
                    else:
                        current_line = ''
                        current_width = 0
            else:
                current_line += char
                current_width += char_w
        # Add the remaining line if there's any text left
        result += current_line

        lines = result.split('\n')
        y = relativeOffset[1] * len(lines) + (len(lines) - 1) * 0.5

        linewidths = list(0 for line in range(len(lines)))
        for k, line in enumerate(lines):
            for char in line:
                linewidths[k] += int(self.sprites[char][1].w * scale[0])
        widest = max(linewidths)

        if align == 1:  # left
            pos = (pos[0] + (widest * (-relativeOffset[0] - 0.5)), pos[1])
        elif align == -1:  # right
            pos = (pos[0] + (widest * (-relativeOffset[0] + 0.5)), pos[1])
        elif align == 0:  # center
            pos = (pos[0] + (widest * (-relativeOffset[0])), pos[1])

        width = 0
        enter = 0
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
                              offset=(linewidths[lk] * 0.5, 0), rotation=rotation, flip=flip, alpha=alpha)
                    width -= w

            width = 0
            enter += self.sprites['A'][1].h

        return linewidths

    def __len__(self):
        return len(self.sprites)
