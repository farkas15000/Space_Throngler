import math
import random

import pygame
from multi_sprite_renderer_normal import MultiSprite as msr
from multi_sprite_renderer_normal import rotated_collision
from entity import Laser
from entity import Box


def dotsrot(start: pygame.math.Vector2, end: pygame.math.Vector2):
    # returns the angle from one point to another
    return pygame.Vector2.angle_to(end-start, (1, 0)) % 360

# 0.6875 scale base
class Monster():

    def __init__(self, game, sprites: msr, scale):
        self.scale = 0.6875 * scale *1.15
        self.game = game
        self.msr = sprites
        self.pos = pygame.Vector2(self.game.width/2, self.game.height/2)
        self.health = 100
        self.speed = 20 * self.scale
        self.armpos = pygame.Vector2(self.game.width / 2, self.game.height / 2)
        self.armspeed = 50 * self.scale
        self.tentacle = Tentacle(self.msr, self.pos, length=16, rot=180, links=12, start=self.armpos, scale=self.scale)
        self.leftleg = Limb(self.msr, self.pos, self.speed, left=-1, scale=self.scale)
        self.rightleg = Limb(self.msr, self.pos, self.speed, left=1, scale=self.scale)
        self.step = 0
        self.blink = 0
        self.wallrect = pygame.rect.Rect(108, 30, 810, 528)
        self.rect = self.msr.draw(0, scale=(1 * self.scale, 1 * self.scale), pos=self.pos, offset=(0, 0))[0]
        #self.collided = pygame.sprite.Group()
        self.bvh = None
        self.hitstaken = 0

    def update(self, dt, move, mousepos):

        if self.health > 0:
            # healing
            self.health += (4.5+(self.game.wave/2)*(len(self.game.astros)/self.game.astroslimit)) * dt
            self.health = min(self.health, 100)

            mouseposvect = pygame.Vector2(mousepos)
        else:
            # dead
            mouseposvect = pygame.Vector2(self.pos)
            move.update(0, 0)

        # movement. IT WORKS, OK?!
        moved = move.copy()
        direction = move.copy()
        direction.x = 0
        direction.y = round(direction.y)
        direction2 = move.copy()
        direction2.x = round(direction2.x)
        direction2.y = 0
        pos = self.pos.copy()
        armpos = self.armpos.copy()
        if self.wallrect.collidepoint(self.pos + move * self.speed * dt * 10):
            pos += move * self.speed * dt * 10
            armpos += move * self.speed * dt * 10
        elif self.wallrect.collidepoint(self.pos + direction * self.speed * dt * 10):
            pos += direction * self.speed * dt * 10
            armpos += direction * self.speed * dt * 10
            moved = direction
        elif self.wallrect.collidepoint(self.pos + direction2 * self.speed * dt * 10):
            pos += direction2 * self.speed * dt * 10
            armpos += direction2 * self.speed * dt * 10
            moved = direction2

        '''if self.collided:
            self.pos.update(pos)
            self.armpos.update(armpos)'''

        rect = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=self.pos, offset=(0, 0))[0]
        for item in self.bvh.collisionrect(rect=rect):
            if isinstance(item, Box) and not item.falling and Box.holding is not item:
                self.pos.update(pos)
                self.armpos.update(armpos)
                break
        else:
            rect = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=pos, offset=(0, 0))[0]
            diry = False
            for item in self.bvh.collisionrect(rect=rect):
                if isinstance(item, Box) and not item.falling and Box.holding is not item:
                    diry = True
                    break
            else:
                self.pos.update(pos)
                self.armpos.update(armpos)
            dirx = False
            if diry:
                pos = self.pos.copy()
                armpos = self.armpos.copy()
                pos += direction * self.speed * dt * 10
                armpos += direction * self.speed * dt * 10
                if self.wallrect.collidepoint(pos):
                    rect = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=pos, offset=(0, 0))[0]
                    for item in self.bvh.collisionrect(rect=rect):
                        if isinstance(item, Box) and not item.falling and Box.holding is not item:
                            dirx = True
                            break
                    else:
                        self.pos.update(pos)
                        self.armpos.update(armpos)
                        moved = direction
                else:
                    dirx = True
            if dirx:
                pos = self.pos.copy()
                armpos = self.armpos.copy()
                pos += direction2 * self.speed * dt * 10
                armpos += direction2 * self.speed * dt * 10
                if self.wallrect.collidepoint(pos):
                    rect = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=pos, offset=(0, 0))[0]
                    for item in self.bvh.collisionrect(rect=rect):
                        if isinstance(item, Box) and not item.falling and Box.holding is not item:
                            moved = pygame.Vector2()
                            break
                    else:
                        self.pos.update(pos)
                        self.armpos.update(armpos)
                        moved = direction2
                else:
                    moved = pygame.Vector2()
        # movement end

        # arm calculation
        if (offset := self.tentacle.endpos - mouseposvect).length_squared() > (self.tentacle.length*2+4)**2:
            self.armpos.move_towards_ip(self.tentacle.endpos + offset.normalize()*-(self.tentacle.length*2+4), self.armspeed * dt * 10)
        else:
            self.armpos.move_towards_ip(mouseposvect, self.armspeed * dt * 10)

        # tentacle
        self.tentacle.update(dt, self.armpos, self.pos)

        # arm debug
        #pygame.draw.rect(self.msr.renderer, (0, 255, 0, 0), (*self.armpos, 8, 8), width=0)
        #pygame.draw.rect(self.msr.renderer, (255, 0, 0, 0), (*self.tentacle.endpos, 8, 8), width=0)

        # legs
        self.leftleg.update(dt, moved, self.rightleg.grounded)
        self.rightleg.update(dt, moved, self.leftleg.grounded)

        self.blink -= dt

        # wall rect debug
        #pygame.draw.rect(self.msr.renderer, (255, 0, 0, 0), self.wallrect, width=1)

        #self.collided.empty()

    def body_draw(self):
        # body
        self.rect = self.msr.draw(0, scale=(1 * self.scale, 1 * self.scale), pos=self.pos, offset=(0, 0))[0]

        # eye
        offset = self.tentacle.endpos - self.pos
        if offset.length_squared() >= 9 * self.scale:
            offset = offset.normalize() * 3 * self.scale
        offset.x *= 1.2
        offset.y *= 0.68
        self.msr.draw(1, scale=(1 * self.scale, 1 * self.scale), pos=self.pos + offset, offset=(0, 0))

        if self.blink <= 0.06 or self.health <= 0:  # blink
            self.msr.draw(3, scale=(2 * self.scale, 2 * self.scale), pos=self.pos, offset=(0, 0))
            if self.blink <= 0:
                self.blink = random.random() * 3 + 2

        # health bar
        self.msr.draw(4, scale=(self.scale/0.6875, 1.5 * self.scale), pos=self.pos, offset=(0, 2.5))
        self.msr.draw(5, scale=(max(self.health/100, 0) * self.scale/0.6875, 1.5 * self.scale), pos=self.pos + (-16 * self.scale/0.6875, 0), offset=(-0.5, 2.5))

    def legs_draw(self):
        self.leftleg.draw()
        self.rightleg.draw()

    def collision(self, hits):
        if hits:
            for item in hits:
                if isinstance(item, Laser) and rotated_collision((self.rect, 0), item.rects):
                    if self.health > 0:
                        self.hitstaken += 1
                    self.health -= item.damage
                    item.die()

                #if isinstance(item, Box) and not item.falling and Box.holding is not item:
                #    self.collided.add(item)

class Limb():

    def __init__(self, sprites, bodypos, bodyspeed, left=-1, scale=1.0):
        self.left = left
        self.msr = sprites
        self.scale = scale
        self.bodypos = bodypos
        self.bodyspeed = bodyspeed
        self.upper = math.ceil(38 * self.scale)
        self.lower = math.ceil(64 * self.scale)
        self.minlen = 34 * self.scale
        self.maxdist = 35 * self.scale
        self.speed = 54 * self.scale
        self.end = self.bodypos+((self.upper*1.2+15 * self.scale)*self.left, self.lower*0.6)  # ending of the leg
        self.next = self.end.copy()
        self.prev = self.end.copy()
        self.grounded = 1

    def update(self, dt, move, step):

        start = self.bodypos+(16*self.left * self.scale, 0)

        limb = self.limb(start, self.end, self.upper, self.lower, self.minlen, flip=self.left < 0)

        # upper limb draw
        #self.msr.draw(name=2, scale=[self.upper / 16, 0.9 * self.scale], pos=limb[0], offset=(-0.5, 0), rotation=limb[1])
        #self.msr.draw(name=2, scale=[self.lower / 16, 0.8 * self.scale], pos=limb[2], offset=(-0.5, 0), rotation=limb[3])

        # lower limb draw
        #self.msr.draw(name=3, scale=[1 * self.scale, 1 * self.scale], pos=start, offset=(0, 0), rotation=limb[1])
        #self.msr.draw(name=3, scale=[0.9 * self.scale, 0.9 * self.scale], pos=limb[2], offset=(0, 0), rotation=limb[3])
        #self.msr.draw(name=3, scale=[1.2 * self.scale, 0.9 * self.scale], pos=limb[4], offset=(0.05, 0), rotation=0)

        limbpos = self.bodypos+((self.upper*1.2+15 * self.scale)*self.left, self.lower*0.6)
        limbdist = (limbpos - limb[4]).length()

        # decide to step
        if (limbdist > self.maxdist or (self.end-self.bodypos).length() > self.maxdist*4 or (self.end.y-self.bodypos.y) < self.maxdist*0.4) and step:
            self.next = limbpos + (move.x*self.bodyspeed*2, move.y*self.bodyspeed*2)
            self.prev.update(self.end)

        # leg debug
        #pygame.draw.rect(self.msr.renderer, (250, 0, 0, 0), (*limbpos, 4, 4), width=1)
        #pygame.draw.rect(self.msr.renderer, (250, 0, 0, 0), (*self.next, 4, 4), width=0)
        #pygame.draw.rect(self.msr.renderer, (0, 250, 0, 0), (*self.end, 4, 4), width=1)
        #pygame.draw.rect(self.msr.renderer, (0, 0, 255, 0), (*self.prev, 4, 4), width=1)

        self.end.move_towards_ip(self.next, self.speed * dt * 10)

        # stepping motion
        if self.prev.x-self.next.x:
            self.end.y = math.sin(abs(self.end.x-self.next.x) / abs(self.prev.x-self.next.x)*math.pi)*-0.06*abs(self.prev.x-self.next.x) + self.end.y

        self.grounded = self.end == self.next

    def draw(self):
        start = self.bodypos + (16 * self.left * self.scale, 0)

        limb = self.limb(start, self.end, self.upper, self.lower, self.minlen, flip=self.left < 0)

        # upper limb draw
        self.msr.draw(name=2, scale=[self.upper / 16, 0.9 * self.scale], pos=limb[0], offset=(-0.5, 0),
                      rotation=limb[1])
        self.msr.draw(name=2, scale=[self.lower / 16, 0.8 * self.scale], pos=limb[2], offset=(-0.5, 0),
                      rotation=limb[3])

        # lower limb draw
        self.msr.draw(name=3, scale=[1 * self.scale, 1 * self.scale], pos=start, offset=(0, 0), rotation=limb[1])
        self.msr.draw(name=3, scale=[0.9 * self.scale, 0.9 * self.scale], pos=limb[2], offset=(0, 0), rotation=limb[3])
        self.msr.draw(name=3, scale=[1.2 * self.scale, 0.9 * self.scale], pos=limb[4], offset=(0.05, 0), rotation=0)

    @staticmethod
    def limb(start: pygame.math.Vector2, end: pygame.math.Vector2, lower: int, upper: int, minlength=0, flip=False):
        # returns: start pos, first rotation, joint pos, second rotation, real end pos, distance from targeted end pos

        aim = end - start
        if aim.x == 0 and aim.y == 0:
            aim = pygame.math.Vector2(1, 0)
        dist = pygame.math.Vector2.length(aim)
        dist = pygame.math.clamp(dist, max(abs(lower - upper), minlength), lower + upper)
        aim = pygame.Vector2.angle_to(aim, (1, 0)) % 360

        urot = math.acos((dist ** 2 - lower ** 2 - upper ** 2) / (2 * lower * upper))
        lrot = math.atan((upper * math.sin(urot)) / (lower + upper * math.cos(urot)))
        urot = math.degrees(urot)
        lrot = math.degrees(lrot)
        if lrot < 0:
            lrot += 180
        if flip:
            lrot *= -1
            urot *= -1
        lowercord = pygame.Vector2(lower, 0).rotate(-lrot - aim) + start
        uppercord = pygame.Vector2(dist, 0).rotate(-aim) + start
        distance = (uppercord - end).length()

        return start, lrot + aim, lowercord, lrot - urot + aim, uppercord, distance


class Tentacle():
    # modified Chain class

    def __init__(self, sprite, end, length, rot, links, start=None, scale=1.0):
        self.msr = sprite
        self.scale = scale
        self.timer = 0
        self.length = length * self.scale
        self.count = links
        self.links = []
        self.reach = length * links * self.scale
        rotate = rot
        for place in range(links):
            vect = pygame.Vector2(self.length, 0).rotate(-rotate)
            if not self.links:
                vect += end
            else:
                vect += self.links[place-1][0]
            self.links.append([vect, rotate])
            rotate += rot

        self.endpos = self.links[0][0]

        if start:
            diff = self.links[-1][0]-start
            for k, (link, rot) in enumerate(self.links):
                link -= diff

    def update(self, dt, end, start=None):

        for k, (link, _) in enumerate(self.links):
            if k == 0:
                rot = dotsrot(end, link)
            else:
                rot = dotsrot(self.links[k-1][0], link)
                end = self.links[k-1][0]
            rot %= 360

            rot += math.sin(k/self.count*16+self.timer*4)*4*dt*45  # wiggle

            link.update(pygame.math.Vector2(self.length, 0).rotate(-rot) + end)
            self.links[k][1] = rot

        if start:
            diff = self.links[-1][0] - start
            for k, (link, _) in enumerate(self.links):
                link -= diff

        self.timer += dt

    def draw(self):
        #cord = pygame.rect.Rect(0, 0, 4, 4)
        for k, (link, rot) in enumerate(self.links):
            self.msr.draw(name=3, scale=[1.4 * self.scale, (0.9+(k*0.05)) * self.scale], pos=link, offset=(0.5, 0), rotation=rot, flip=[0, 0])

            #debug
            #cord.center = link
            #pygame.draw.rect(self.msr.renderer, (250, 0, 0, 0), cord, width=0)

