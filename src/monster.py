import math
import random

import pygame

from buttons import Button
from multi_sprite_renderer_hardware import MultiSprite as Msr, rotated_collision
from entity import Laser
from entity import Box
from engine import StateMachine as Sm


def dotsRot(start: pygame.math.Vector2, end: pygame.math.Vector2):
    """returns the angle from one point to another"""
    return pygame.Vector2.angle_to(end-start, (1, 0)) % 360


class Monster:

    def __init__(self, sprites: Msr, scale):
        self.game = Sm.states["game_instance"]
        self.scale = 0.6875 * scale * 1.15
        self.msr = sprites
        self.pos = pygame.Vector2(Sm.app.logical_sizeRect.size) / 2
        self.health = 100
        self.speed = 20 * self.scale
        self.armPos = pygame.Vector2(Sm.app.logical_sizeRect.size) / 2
        self.armSpeed = 50 * self.scale
        self.tentacle = Tentacle(self.msr, self.pos, length=16, rot=180, links=12, start=self.armPos, scale=self.scale)
        self.leftLeg = Limb(self.msr, self.pos, self.speed, left=-1, scale=self.scale)
        self.rightLeg = Limb(self.msr, self.pos, self.speed, left=1, scale=self.scale)
        self.step = 0
        self.blink = 0
        self.wallRect = pygame.rect.Rect(108, 30, 810, 528)
        self.rect = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=self.pos, relativeOffset=(0, 0))[0]
        self.bvh = None
        self.hitsTaken = 0

    def update(self, dt):

        # keyboard control
        move = pygame.Vector2(0, 0)
        keys = Sm.app.keyboard[1]
        if keys[Sm.app.controls['Left']] or keys[pygame.K_LEFT]:
            move.x += 1
        if keys[Sm.app.controls['Right']] or keys[pygame.K_RIGHT]:
            move.x -= 1
        if keys[Sm.app.controls['Up']] or keys[pygame.K_UP]:
            move.y += 1
        if keys[Sm.app.controls['Down']] or keys[pygame.K_DOWN]:
            move.y -= 1
        if move.x != 0 or move.y != 0:
            move = move.normalize()
            move *= -1

        # mouse/touch control
        if Sm.app.mobile:
            if self.pos.distance_squared_to(Button.mousePos[1]) > (192 / 2.5 * 0.6875)**2:
                vect = self.pos - Button.mousePos[1]
                if vect.x != 0 or vect.y != 0:
                    vect = vect.normalize()
                    vect *= -1
                move.xy = vect
            else:
                move.update(0, 0)

        if self.health > 0:
            # healing
            self.health += (4.5 + (self.game.wave/2) * (len(self.game.astros) / self.game.astrosLimit)) * dt
            self.health = min(self.health, 100)

            mouse_pos_vect = pygame.Vector2(Button.mousePos[1])
        else:
            # dead
            mouse_pos_vect = pygame.Vector2(self.pos)
            move.update(0, 0)

        # movement
        moved = move.copy()
        direction = move.copy()
        direction.x = 0
        direction.y = round(direction.y)
        direction2 = move.copy()
        direction2.x = round(direction2.x)
        direction2.y = 0
        pos = self.pos.copy()
        arm_pos = self.armPos.copy()
        if self.wallRect.collidepoint(self.pos + move * self.speed * dt * 10):
            pos += move * self.speed * dt * 10
            arm_pos += move * self.speed * dt * 10
        elif self.wallRect.collidepoint(self.pos + direction * self.speed * dt * 10):
            pos += direction * self.speed * dt * 10
            arm_pos += direction * self.speed * dt * 10
            moved = direction
        elif self.wallRect.collidepoint(self.pos + direction2 * self.speed * dt * 10):
            pos += direction2 * self.speed * dt * 10
            arm_pos += direction2 * self.speed * dt * 10
            moved = direction2

        rect = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=self.pos, relativeOffset=(0, 0))[0]
        for item in self.bvh.collisionRect(rect=rect):
            if isinstance(item, Box) and not item.falling and Box.holding is not item:
                self.pos.update(pos)
                self.armPos.update(arm_pos)
                break
        else:
            rect = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=pos, relativeOffset=(0, 0))[0]
            diry = False
            for item in self.bvh.collisionRect(rect=rect):
                if isinstance(item, Box) and not item.falling and Box.holding is not item:
                    diry = True
                    break
            else:
                self.pos.update(pos)
                self.armPos.update(arm_pos)
            dirx = False
            if diry:
                pos = self.pos.copy()
                arm_pos = self.armPos.copy()
                pos += direction * self.speed * dt * 10
                arm_pos += direction * self.speed * dt * 10
                if self.wallRect.collidepoint(pos):
                    rect = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=pos, relativeOffset=(0, 0))[0]
                    for item in self.bvh.collisionRect(rect=rect):
                        if isinstance(item, Box) and not item.falling and Box.holding is not item:
                            dirx = True
                            break
                    else:
                        self.pos.update(pos)
                        self.armPos.update(arm_pos)
                        moved = direction
                else:
                    dirx = True
            if dirx:
                pos = self.pos.copy()
                arm_pos = self.armPos.copy()
                pos += direction2 * self.speed * dt * 10
                arm_pos += direction2 * self.speed * dt * 10
                if self.wallRect.collidepoint(pos):
                    rect = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=pos, relativeOffset=(0, 0))[0]
                    for item in self.bvh.collisionRect(rect=rect):
                        if isinstance(item, Box) and not item.falling and Box.holding is not item:
                            moved = pygame.Vector2()
                            break
                    else:
                        self.pos.update(pos)
                        self.armPos.update(arm_pos)
                        moved = direction2
                else:
                    moved = pygame.Vector2()
        # movement end

        # arm calculation
        if (relativeOffset := self.tentacle.endPos - mouse_pos_vect).length_squared() > (self.tentacle.length * 2 + 4)**2:
            self.armPos.move_towards_ip(self.tentacle.endPos + relativeOffset.normalize() * -(self.tentacle.length * 2 + 4), self.armSpeed * dt * 10)
        else:
            self.armPos.move_towards_ip(mouse_pos_vect, self.armSpeed * dt * 10)

        # tentacle
        self.tentacle.update(dt, self.armPos, self.pos)

        # legs
        self.leftLeg.update(dt, moved, self.rightLeg.grounded)
        self.rightLeg.update(dt, moved, self.leftLeg.grounded)

        self.blink -= dt

    def body_draw(self):
        # body
        rects = self.msr.rects(0, scale=(1 * self.scale, 1 * self.scale), pos=self.pos, relativeOffset=(0, 0))
        self.rect = rects[0]
        self.msr.draw_only(0, rects)

        # eye
        offset = self.tentacle.endPos - self.pos
        if offset.length_squared() >= 9 * self.scale:
            offset = offset.normalize() * -3 * self.scale
        offset.x *= 1.2
        offset.y *= 0.68
        self.msr.draw(1, scale=(1 * self.scale, 1 * self.scale), pos=self.pos, relativeOffset=(0, 0), offset=offset)

        # blink
        if self.blink <= 0.06 or self.health <= 0:
            self.msr.draw(3, scale=(2 * self.scale, 2 * self.scale), pos=self.pos, relativeOffset=(0, 0))
            if self.blink <= 0:
                self.blink = random.random() * 3 + 2

        # health bar
        self.msr.draw(4, scale=(self.scale/0.6875, 1.5 * self.scale), pos=self.pos, relativeOffset=(0, 2.5))
        self.msr.draw(5, scale=(max(self.health/100, 0) * self.scale/0.6875, 1.5 * self.scale), pos=self.pos + (-16 * self.scale/0.6875, 0), relativeOffset=(-0.5, 2.5), offset=(-0.4, 0))

    def legs_draw(self):
        self.leftLeg.draw()
        self.rightLeg.draw()

    def collision(self, hits):
        if hits:
            for item in hits:
                if isinstance(item, Laser) and rotated_collision((self.rect, 0), item.rects):
                    if self.health > 0:
                        self.hitsTaken += 1
                    self.health -= item.damage
                    item.die()


class Limb:

    def __init__(self, sprites, body_pos, body_speed, left=-1, scale=1.0):
        self.left = left
        self.msr = sprites
        self.scale = scale
        self.bodyPos = body_pos
        self.bodySpeed = body_speed
        self.upper = math.ceil(38 * self.scale)
        self.lower = math.ceil(64 * self.scale)
        self.minLen = round(34 * self.scale)
        self.maxDist = 35 * self.scale
        self.speed = 54 * self.scale
        self.end = self.bodyPos + ((self.upper * 1.2 + 15 * self.scale) * self.left, self.lower * 0.6)  # ending of the leg
        self.next = self.end.copy()
        self.prev = self.end.copy()
        self.grounded = 1

    def update(self, dt, move, step):

        start = self.bodyPos + (16 * self.left * self.scale, 0)

        limb = self.limb(start, self.end, self.upper, self.lower, self.minLen, flip=self.left < 0)

        limb_pos = self.bodyPos + ((self.upper * 1.2 + 15 * self.scale) * self.left, self.lower * 0.6)
        limb_dist = (limb_pos - limb[4]).length()

        # decide to step
        if (limb_dist > self.maxDist or (self.end - self.bodyPos).length() > self.maxDist * 4 or (self.end.y - self.bodyPos.y) < self.maxDist * 0.4) and step:
            self.next = limb_pos + (move.x * self.bodySpeed * 2, move.y * self.bodySpeed * 2)
            self.prev.update(self.end)

        self.end.move_towards_ip(self.next, self.speed * dt * 10)

        # stepping motion
        if self.prev.x-self.next.x:
            self.end.y = math.sin(abs(self.end.x-self.next.x) / abs(self.prev.x-self.next.x)*math.pi)*-0.06*abs(self.prev.x-self.next.x) + self.end.y

        self.grounded = self.end == self.next

    def draw(self):
        start = self.bodyPos + (16 * self.left * self.scale, 0)

        limb = self.limb(start, self.end, self.upper, self.lower, self.minLen, flip=self.left < 0)

        # upper limb draw
        self.msr.draw(name=2, scale=[self.upper / 16, 0.9 * self.scale], pos=limb[0], relativeOffset=(-0.5, 0),
                      rotation=limb[1])
        self.msr.draw(name=2, scale=[self.lower / 16, 0.8 * self.scale], pos=limb[2], relativeOffset=(-0.5, 0),
                      rotation=limb[3])

        # lower limb draw
        self.msr.draw(name=3, scale=[1 * self.scale, 1 * self.scale], pos=start, relativeOffset=(0, 0), rotation=limb[1])
        self.msr.draw(name=3, scale=[0.9 * self.scale, 0.9 * self.scale], pos=limb[2], relativeOffset=(0, 0), rotation=limb[3])
        self.msr.draw(name=3, scale=[1.2 * self.scale, 0.9 * self.scale], pos=limb[4], relativeOffset=(0.05, 0), rotation=0)

    @staticmethod
    def limb(start: pygame.math.Vector2, end: pygame.math.Vector2, lower: int, upper: int, min_length=0, flip=False):
        """
        returns: start pos, first rotation, joint pos, second rotation, real end pos, distance from targeted end pos
        """

        aim = end - start
        if aim.x == 0 and aim.y == 0:
            aim = pygame.math.Vector2(1, 0)
        dist = pygame.math.Vector2.length(aim)
        dist = pygame.math.clamp(dist, max(abs(lower - upper), min_length), lower + upper)
        aim = pygame.Vector2.angle_to(aim, (1, 0)) % 360

        # source: https://i.ytimg.com/vi/IKOGwoJ2HLk/maxresdefault.jpg
        u_rot = math.acos((dist ** 2 - lower ** 2 - upper ** 2) / (2 * lower * upper))
        l_rot = math.atan((upper * math.sin(u_rot)) / (lower + upper * math.cos(u_rot)))
        u_rot = math.degrees(u_rot)
        l_rot = math.degrees(l_rot)
        if l_rot < 0:
            l_rot += 180
        if flip:
            l_rot *= -1
            u_rot *= -1
        lower_cord = pygame.Vector2(lower, 0).rotate(-l_rot - aim) + start
        upper_cord = pygame.Vector2(dist, 0).rotate(-aim) + start
        distance = (upper_cord - end).length()

        return start, l_rot + aim, lower_cord, l_rot - u_rot + aim, upper_cord, distance


class Tentacle:
    """modified Chain class for monster tentacle"""

    def __init__(self, sprites, end, length, rot, links, start=None, scale=1.0):
        self.msr = sprites
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

        self.endPos = self.links[0][0]

        if start:
            diff = self.links[-1][0]-start
            for k, (link, rot) in enumerate(self.links):
                link -= diff

    def update(self, dt, end, start=None):

        for k, (link, _) in enumerate(self.links):
            if k == 0:
                rot = dotsRot(end, link)
            else:
                rot = dotsRot(self.links[k - 1][0], link)
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
        for k, (link, rot) in enumerate(self.links):
            self.msr.draw(name=3, scale=[1.4 * self.scale, (0.9+(k*0.05)) * self.scale], pos=link, relativeOffset=(0.5, 0), rotation=rot, flip=[0, 0])
