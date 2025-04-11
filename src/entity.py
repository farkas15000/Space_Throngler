import math
import random

import pygame

from buttons import Button
from particles import Particle
from assets import Assets


def dotsRot(start: pygame.math.Vector2, end: pygame.math.Vector2):
    """returns the angle from one point to another"""
    return pygame.Vector2.angle_to(end - start, (1, 0)) % 360


def map_value(value, value_min, value_max, map_min, map_max):
    return ((value - value_min) / (value_max - value_min)) * (
        map_max - map_min
    ) + map_min


class Box(Button, pygame.sprite.Sprite):
    tentaclePos = None
    tentacleMouse = None
    dt = None
    holding = None
    reached = 0
    particles = None
    thrown = 0

    @classmethod
    def tentacle(cls, dt, tentacle_pos, tentacle_mouse, reached):
        """tentacle data getter"""
        cls.tentaclePos = tentacle_pos
        cls.tentacleMouse = tentacle_mouse
        cls.dt = dt
        cls.reached = reached

    def __init__(self, sprites, sounds, hit_sounds):
        self.falling = True
        x = random.randint(162, 842)
        self.pos = pygame.Vector2(x, -30)
        self.target = pygame.Vector2(x, random.randint(50, 544))
        self.speed = 25
        self.base_health = 100
        self.health = self.base_health
        self.thrown = 0
        self.sounds = sounds
        self.hitSounds = hit_sounds
        super().__init__(sprites=sprites, pos=self.pos, scale=(2, 2))
        self.rect = self.rects[0]
        self.grabPos = pygame.Vector2()
        self.releasePos = self.target.copy()
        self.vectors = [(self.target.copy(), 0)]
        self.timer = 0
        self.bleeds = []
        self.firstLanded = False
        self.windTimer = 0
        self.wallRect = pygame.rect.Rect(98, 16, 828, 550)
        self.destruct = 14 + random.random() * 2

    def update(self, mode=None):
        match mode:
            case "draw":
                self.draw(0)
            case "shadow":
                self.drawShadow()
            case _:
                self.run()

    def run(self):

        self.rects = self.sprites.rects(
            name=self.name,
            scale=(self.xm, self.ym),
            pos=self.pos,
            relativeOffset=self.relativeOffset,
        )
        self.rect = self.rects[0]

        # wall hit handle
        drop = False
        if self.firstLanded and not self.wallRect.contains(self.rect):
            drop = True
            self.thrown += 1
            rect = self.rect.scale_by(1.1)
            self.target.update(rect.clamp(self.wallRect).center)
            self.pos.update(self.target)

            self.vectors.clear()
            self.vectors.append((self.target.copy(), self.timer))

        # damaged sprite selection
        self.name = min(3, 3 - round((self.health / self.base_health) * 3))

        mouse_pos = (
            Box.tentaclePos[0]
            + (Button.mousePos[0] - Box.tentaclePos[0]).normalize() * 8,
            Box.tentaclePos[1]
            + (Button.mousePos[1] - Box.tentaclePos[1]).normalize() * 8,
        )
        mouse = Box.tentacleMouse
        dt = Box.dt
        self.timer += dt
        self.destruct -= dt * (self.thrown + 1)
        self.windTimer -= dt

        # update the button parts
        sticked = self.sticked
        unstick = Box.holding and Box.holding is not self
        self.loop(
            draw=False,
            mouse_pos=mouse_pos,
            mouse=mouse,
            unstick=drop or unstick or self.falling,
        )
        self.rect = self.rects[0]

        # grab box
        if not Box.holding or Box.holding is self:

            if not self.falling and self.sticked:
                Box.holding = self
                self.destruct = 15

                if self.sticked and not sticked:
                    self.grabPos = self.pos - mouse_pos[1]
                    self.vectors.clear()

                self.pos.update(mouse_pos[1] + self.grabPos)

                if not self.vectors:
                    self.vectors.append((self.pos.copy(), self.timer))

                if (
                    self.timer - self.vectors[-1][1] >= 0.0005 / Box.dt
                ):  # frame rate independent magic number
                    self.vectors.append((self.pos.copy(), self.timer))
                if len(self.vectors) > 5:
                    self.vectors.pop(0)

            # box throw
            if (not self.sticked and sticked) and Box.holding is self:
                Box.holding = None
                self.falling = True
                self.releasePos.update(self.pos)

                if drop:
                    self.speed = 25
                else:
                    self.speed = max(self.targeting() / 2.6, 25)
                    if self.speed >= 30:
                        Box.thrown += 1
                        self.thrown += 1

                self.vectors.clear()
                self.vectors.append((self.target.copy(), self.timer))

        if self.falling:
            self.pos.move_towards_ip(self.target, self.speed * dt * 10)

            self.wind()

            # fake physics
            if self.pos.x - self.target.x:
                self.pos.y = (
                    math.sin(
                        abs(self.pos.x - self.target.x)
                        / abs(self.releasePos.x - self.target.x)
                        * math.pi
                    )
                    * -0.4
                    * abs(self.releasePos.x - self.target.x)
                    / self.speed
                    + self.pos.y
                )

            self.falling = self.pos != self.target

            self.destruct = 15

            if not self.falling:  # target reached
                self.firstLanded = True

                # damaged
                if self.speed >= 30:
                    self.health -= self.speed
                    random.choice(self.sounds).play()

        if self.health <= 0 or self.destruct <= 0:
            self.die()

    def die(self):
        if Box.holding is self:
            Box.holding = None

        self.kill()

        for z in range(random.randrange(8, 10)):
            particle = Particle(
                pos=self.pos,
                sprites=Assets.particleSprites,
                animation=(0.8, 20 + random.randrange(5)),
                velocity=pygame.Vector2(-random.randint(50, 70), 0).rotate(
                    (random.randint(0, 180))
                ),
                scale=(2, 2),
                rotation=random.randrange(10) * 36,
                relativeOffset=(random.uniform(-1, 1), random.uniform(-1, 1)),
                turn=random.randint(-60, 60),
            )
            Box.particles.add(particle)

    def wind(self):
        if (
            self.windTimer <= 0
            and self.speed >= 30
            and (aim := (self.pos - self.target))
        ):
            self.windTimer = random.uniform(0.03, 0.05)

            vel = aim.normalize().rotate(
                random.randint(-10, 10)
            ) * random.randint(200, 300)

            particle = Particle(
                pos=self.pos
                + (random.randint(-11, 11), random.randint(-11, 11)),
                sprites=Assets.particleSprites,
                animation=(0.15, 2),
                velocity=vel,
                scale=(3, 3),
                rotation=dotsRot(vel, pygame.Vector2(1, 0)),
            )
            Box.particles.add(particle)

    def targeting(self):
        # where to land
        target = pygame.Vector2()

        for vec, _ in self.vectors:
            target += vec - self.vectors[0][0]

        target = target * (length := target.length()) / 40

        self.target.update(target + self.vectors[0][0])

        return length

    def collision(self, hits):
        for item in hits:
            if isinstance(item, Laser):
                if self == Box.holding:
                    self.health -= 5
                else:
                    self.health -= 10
                item.die()

    def draw(self, rects=1):
        # box
        if rects:
            self.rects = self.sprites.rects(
                name=self.name,
                scale=(self.xm, self.ym),
                pos=self.pos,
                relativeOffset=self.relativeOffset,
            )
        self.sprites.draw_only(
            name=self.name, rects=self.rects, scale=(self.xm, self.ym)
        )

        # blood
        for blood in self.bleeds:
            Assets.bloodSprites.draw(
                name=blood[0],
                scale=(2.5, 2.5),
                pos=self.pos + blood[1],
                rotation=blood[2],
                flip=blood[3],
            )

        # outline
        if (
            self.onNow and not self.falling and Box.holding is None
        ) or Box.holding is self:
            self.sprites.draw(
                name=4,
                scale=(self.xm, self.ym),
                pos=self.rects[0].center,
                relativeOffset=self.relativeOffset,
            )

    def drawShadow(self):
        if not self.firstLanded:
            self.sprites.draw(
                name=5,
                scale=(self.xm, self.ym),
                pos=self.target,
                relativeOffset=(0, 0),
                alpha=(
                    (self.pos.y - self.target.y) / (self.target.y + 30) + 1
                ),
            )


class Astronaut(pygame.sprite.Sprite):
    monster = None
    deathAnim = None
    died = 0

    def __init__(self, sprites, health, damage):
        super().__init__()
        self.msr = sprites
        self.scale = 2
        start_gate = random.randrange(4)
        gates = [(52, 150), (52, 448), (972, 150), (972, 450)]
        self.monster = Astronaut.monster
        self.pos = pygame.Vector2(gates[start_gate])
        self.target = pygame.Vector2(
            self.pos
            + pygame.Vector2(
                (1 if (flip_x := self.pos.x < self.monster.pos.x) else -1)
                * 70,
                random.randrange(-30, 30),
            )
        )
        self.distance = self.pos.distance_to(self.target)
        self.chainStart = self.target.copy()
        self.chain = Chain(self.chainStart, 10, 180, 5)
        self.speed = 5
        self.health = health
        self.damage = damage
        self.frame = 0
        self.animation = {"walk": [self.speed / 4, 2, 3, 4, 5]}
        self.animTimer = random.random()
        self.flipX = not flip_x
        self.rects = self.msr.rects(
            name=self.frame,
            scale=(self.scale, self.scale),
            pos=self.pos,
            relativeOffset=(0, 0),
        )
        self.rect = self.rects[0]
        self.bloodTimer = 0
        self.shootTimer = random.random() + 1
        self.wallRect = pygame.rect.Rect(100, 16, 824, 548)
        self.collided = pygame.sprite.Group()
        self.bleeds = []

    def update(self, mode=None):
        match mode:
            case "draw":
                self.draw()
            case _:
                self.run()

    def run(self):
        dt = Box.dt
        self.shootTimer -= dt

        if self.health <= 0:
            self.die()

        self.pos.move_towards_ip(self.target, self.speed * dt * 10)

        self.distance = self.pos.distance_to(self.target)
        self.rects = self.msr.rects(
            name=self.frame,
            scale=(self.scale, self.scale),
            pos=self.pos,
            relativeOffset=(0, 0),
        )
        self.rect = self.rects[0]

        self.shoot()
        self.animator("walk")

        if abs(self.pos.x - self.monster.pos.x) > 30:
            self.flipX = self.pos.x > self.monster.pos.x

        if self.pos == self.target:  # target reached
            self.targeting()

    def targeting(self):
        """updates the chain that the Astronaut follows"""

        step_size = 10
        for z in range(3):
            if vec := (self.chainStart - self.chain.links[1][0]):
                chain_start = self.chainStart + vec.normalize().rotate(
                    random.randint(-110 - z * 35, 110 + z * 35)
                ) * (step_size + z)
            else:
                chain_start = self.chainStart + pygame.Vector2(
                    step_size + z, 0
                ).rotate(random.randrange(360))

            if self.wallRect.collidepoint(chain_start):
                self.chainStart.update(chain_start)
                self.chain.update(self.chainStart)
                self.target.update(self.chain.startPos)
                break
        else:
            self.chainStart.update(self.target)
            self.chain.update(self.chainStart)
            self.target.update(self.chain.startPos)
            if not self.wallRect.collidepoint(self.chainStart):
                vec = (
                    pygame.Vector2(self.pos - self.monster.pos).normalize()
                    * self.speed
                    * Box.dt
                    * -10
                )
                self.pos += vec
                self.chainStart += vec
                self.target += vec
                for link in self.chain.links:
                    link[0] += vec

    def shoot(self):
        if self.shootTimer <= 0:
            Laser(
                self.pos + (-12 if self.flipX else 12, -2), damage=self.damage
            )
            self.shootTimer = random.random() + 1

            for z in range(8):
                particle = Particle(
                    pos=self.pos + (-8 if self.flipX else 8, -2),
                    sprites=Assets.particleSprites,
                    animation=(0.24, 10, 10, 11, 12, 13),
                    velocity=pygame.Vector2(
                        -150 if self.flipX else 150, 0
                    ).rotate((random.randint(-10, 10))),
                    scale=(2, 2),
                    rotation=random.randrange(10) * 36,
                )
                Laser.particles.add(particle)

    def die(self):
        self.kill()
        Astronaut.died += 1

        death = Particle(
            pos=self.pos,
            sprites=self.msr,
            animation=(0.55, 6, 7, 8, 9, 10, 11, 11),
            velocity=(0, 0),
            scale=(self.scale, self.scale),
        )
        death.flipX = self.flipX
        Astronaut.deathAnim.add(death)

    def draw(self):
        self.msr.draw_only(
            name=self.frame,
            rects=self.rects,
            scale=(self.scale, self.scale),
            flip=(self.flipX, 0),
        )

        for blood in self.bleeds:
            Assets.bloodSprites.draw(
                name=blood[0],
                scale=(self.scale, self.scale),
                pos=self.pos + blood[1],
                rotation=blood[2],
                flip=blood[3],
            )

    def animator(self, animation):
        """updates the animation frames
        returns True when a lupe is finished"""

        length = len(self.animation[animation]) - 1
        full = self.animation[animation][0]
        duration = full / length
        self.frame = self.animation[animation][
            int((self.animTimer // duration) % length + 1)
        ]
        self.animTimer += Box.dt
        if self.animTimer >= full:
            self.animTimer %= full
            return True
        return False

    def collision(self, hits):

        if hits:
            if Box.holding and Box.holding in self.collided:
                self.collided.remove(Box.holding)

            collided = {*self.collided}
            new_hits = hits.difference(collided)

            for item in new_hits:
                if isinstance(item, Box):

                    # box collision resolve
                    if (
                        not_held := Box.holding is not item
                    ) and not item.falling:
                        if self.distance < 16:
                            if vec := (self.target - item.pos):
                                self.target += vec.normalize() * Box.dt * 100
                                self.chainStart += (
                                    vec.normalize() * Box.dt * 100
                                )

                    # damaged by melee attack
                    if not not_held:
                        self.health -= 45 * Box.dt
                        self.bloodTimer -= Box.dt

                        if not self.bleeds:
                            self.bleeds.append(
                                (
                                    random.randrange(6),
                                    (
                                        random.uniform(
                                            -4 * self.scale, 4 * self.scale
                                        ),
                                        random.uniform(
                                            -4 * self.scale, 5 * self.scale
                                        ),
                                    ),
                                    random.randrange(10) * 36,
                                    (
                                        random.getrandbits(1),
                                        random.getrandbits(1),
                                    ),
                                )
                            )

                        if self.bloodTimer <= 0:
                            self.bloodTimer = random.uniform(0.05, 0.1)
                            blood = Particle(
                                pos=self.pos
                                + (
                                    random.uniform(
                                        -4 * self.scale, 4 * self.scale
                                    ),
                                    random.uniform(
                                        -4 * self.scale, 5 * self.scale
                                    ),
                                ),
                                sprites=Assets.particleSprites,
                                animation=(0.3, 19, 19, 18),
                                velocity=pygame.Vector2(100, 0).rotate(
                                    rot := (random.randrange(360))
                                ),
                                scale=(2, 2),
                                rotation=rot,
                            )
                            Laser.particles.add(blood)

                    # damaged by thrown box
                    if item.falling and item.speed >= 30:
                        self.health -= item.speed

                        random.choice(item.hitSounds).play()

                        # perma blood on Astronaut
                        if not_held:
                            self.bleeds.append(
                                (
                                    random.randrange(6),
                                    (
                                        random.uniform(
                                            -4 * self.scale, 4 * self.scale
                                        ),
                                        random.uniform(
                                            -4 * self.scale, 5 * self.scale
                                        ),
                                    ),
                                    random.randrange(10) * 36,
                                    (
                                        random.getrandbits(1),
                                        random.getrandbits(1),
                                    ),
                                )
                            )
                            if len(self.bleeds) > 4:
                                self.bleeds.pop(0)

                        # blood on box
                        item.bleeds.append(
                            (
                                random.randrange(6),
                                (random.uniform(-7, 7), random.uniform(-7, 7)),
                                random.randrange(10) * 36,
                                (random.getrandbits(1), random.getrandbits(1)),
                            )
                        )
                        if len(item.bleeds) > 3:
                            item.bleeds.pop(0)

                        # on hit blood
                        for z in range(round(item.speed / 7.5)):
                            blood = Particle(
                                pos=self.pos
                                + (
                                    random.uniform(
                                        -4 * self.scale, 4 * self.scale
                                    ),
                                    random.uniform(
                                        -4 * self.scale, 5 * self.scale
                                    ),
                                ),
                                sprites=Assets.particleSprites,
                                animation=(0.4, 19, 19, 18),
                                velocity=pygame.Vector2(100, 0).rotate(
                                    rot := (random.randrange(360))
                                ),
                                scale=(2, 2),
                                rotation=rot,
                            )
                            Laser.particles.add(blood)

                        # blood on floor
                        for z in range(3):
                            blood = Particle(
                                pos=self.pos
                                + (
                                    random.uniform(
                                        -7 * self.scale, 7 * self.scale
                                    ),
                                    random.uniform(
                                        -5 * self.scale, 9 * self.scale
                                    ),
                                ),
                                sprites=Assets.bloodSprites,
                                animation=(
                                    random.uniform(10, 13),
                                    random.randrange(6),
                                ),
                                velocity=pygame.Vector2(),
                                scale=(3, 3),
                                rotation=random.randrange(360),
                            )
                            self.monster.game.floorBloodParticles.add(blood)

                        if not_held:
                            collided.add(item)

                # Astronaut collision resolve
                if isinstance(item, Astronaut) and (
                    vec := (self.target - item.pos)
                ):
                    self.target += vec.normalize() * Box.dt * 80
                    self.chainStart += vec.normalize() * Box.dt * 80

            collided.intersection_update(hits)
            self.collided.empty()
            self.collided.add(collided)


class Laser(pygame.sprite.Sprite):
    group = None
    particles = None
    wallRect = pygame.rect.Rect(102, 32, 820, 532)

    def __init__(self, pos, damage):
        super().__init__()
        Laser.group.add(self)
        self.scale = 2
        self.msr = Assets.laserSprites
        self.damage = damage
        self.speed = 25
        self.pos = pos.copy()
        aim_rand = pygame.Vector2(random.randrange(16), 0).rotate(
            random.randrange(360)
        )
        self.rotation = dotsRot(Astronaut.monster.pos + aim_rand, self.pos)
        self.direction: pygame.Vector2 = (
            Astronaut.monster.pos + aim_rand - self.pos
        )
        self.rects = self.msr.rects(
            name=0,
            scale=(self.scale, self.scale),
            pos=self.pos,
            relativeOffset=(0, 0),
            rotation=self.rotation,
        )
        self.rect = self.rects[2]
        random.choice(Assets.laserSounds).play()
        if self.direction:
            self.direction.normalize_ip()
        else:
            self.die()

    def update(self, mode=None):
        match mode:
            case "draw":
                self.draw()
            case _:
                self.run()

    def run(self):
        dt = Box.dt

        self.pos += self.direction * self.speed * dt * 10

        self.rects = self.msr.rects(
            name=0,
            scale=(self.scale, self.scale),
            pos=self.pos,
            relativeOffset=(0, 0),
            rotation=self.rotation,
        )
        self.rect = self.rects[2]

        if not self.wallRect.colliderect(self.rect):
            self.die(False)

        self.draw()

    def draw(self):
        self.msr.draw_only(
            name=0,
            rects=self.rects,
            scale=(self.scale, self.scale),
            flip=(0, 0),
        )

    def die(self, sound=True):
        self.kill()

        for z in range(random.randrange(6, 8)):
            particle = Particle(
                pos=self.pos + self.direction * self.speed * Particle.dt * 20,
                sprites=Assets.particleSprites,
                animation=(0.1, 10, 11, 12, 13),
                velocity=(self.direction * -200).rotate(
                    (random.randint(-100, 100))
                ),
                scale=(2, 2),
                rotation=random.randrange(10) * 36,
            )
            Laser.particles.add(particle)

        if sound:
            random.choice(Assets.laserHitSounds).play()

    def collision(self, hits):
        pass


class Chain:
    """chain for Astronaut movement"""

    def __init__(self, end, length, rot, links, start=None, scale=1.0):
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
                vect += self.links[place - 1][0]
            self.links.append([vect, rotate])
            rotate += rot

        self.endPos = self.links[0][0]
        self.startPos = self.links[-1][0]

        if start:
            diff = self.links[-1][0] - start
            for k, (link, rot) in enumerate(self.links):
                link -= diff

    def update(self, end, start=None):

        for k, (link, _) in enumerate(self.links):
            if k == 0:
                rot = dotsRot(end, link)
            else:
                rot = dotsRot(self.links[k - 1][0], link)
                end = self.links[k - 1][0]

            link.update(pygame.math.Vector2(self.length, 0).rotate(-rot) + end)
            self.links[k][1] = rot

        if start:
            diff = self.links[-1][0] - start
            for k, (link, _) in enumerate(self.links):
                link -= diff
