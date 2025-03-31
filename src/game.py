import copy
import random
from datetime import timedelta

import pygame

import entity
from BVH import BVH
from engine import StateMachine as Sm
from buttons import Button

from assets import Assets
from monster import Monster
from particles import Particle


class Game:

    def __init__(self):
        Sm.state = "game"
        Sm.states.update({'game': self.game,
                          'pause': self.pause,
                          'game_instance': self
                          })

        self.menu = Sm.states["menu_instance"]
        self.scene = Sm.states["scene_instance"]

        self.boxes = self.scene.boxes
        self.boxparticles = self.scene.boxparticles
        self.laserparticles = self.scene.rocketparticles
        self.timer = 0
        self.clearedtimer = 0
        entity.Astronaut.died = 0
        entity.Box.thrown = 0

        self.move = pygame.Vector2(0, 0)

        self.sizehalf = pygame.Vector2(Sm.app.logical_sizeRect.size) / 2

        self.pausebutton = Button(sprites=Assets.pausesprites, name=0, scale=(2, 2), pos=(0, 601), relativeOffset=(-0.5, 0.5), popup=(1.06, 1.06))

        self.exitbutton = Button(sprites=Assets.buttonsprites, name=0, scale=(2, 2), relativeOffset=(-0.5, -0.5),
                                 popup=(1.06, 1.06))
        self.exitbutton.scale = (2, 2)

        self.monster = Monster(Assets.monstersprites, Sm.app.scale)
        entity.Astronaut.monster = self.monster

        self.astros = pygame.sprite.Group()
        self.astrosdeathanim = pygame.sprite.Group()
        entity.Astronaut.deathanim = self.astrosdeathanim

        self.lasers = pygame.sprite.Group()
        entity.Laser.group = self.lasers

        self.rocketparticles = self.scene.rocketparticles
        entity.Laser.particles = self.rocketparticles

        self.floorbloodparticles = pygame.sprite.Group()

        self.bvh_maxdepth = 5
        self.bvh = BVH(self.bvh_maxdepth, [self.monster, *self.boxes, *self.astros, *self.lasers])
        self.monster.bvh = self.bvh

        self.asteroidparticles = pygame.sprite.Group()
        left = Particle(pos=self.sizehalf, sprites=Assets.asteroidsprites,
                        animation=(0.6, 1),
                        velocity=(-150, -100),
                        scale=(2, 2), turn=60)
        right = Particle(pos=self.sizehalf, sprites=Assets.asteroidsprites,
                         animation=(0.6, 2),
                         velocity=(150, -100),
                         scale=(2, 2), turn=-60)
        self.asteroidparticles.add(left, right)

        self.wave = 1
        self.nextwave = 2

        self.boxlimit = 3
        self.boxtimer = 1

        self.astroslimit = 2
        self.astrostimer = 1.5
        self.astroshealth = 100
        self.astrosdamage = 10

    def game(self):
        self.dt = Sm.app.dt

        Sm.states["menu_instance"].startimer -= self.dt
        Sm.states["scene_instance"].rockettimer -= self.dt

        if len(self.boxes) < self.boxlimit:
            self.boxtimer -= self.dt
        if self.boxtimer <= 0:
            self.boxtimer = 1
            self.boxes.add(entity.Box(Assets.boxsprites, Assets.boxsounds, Assets.boxhitsounds))

        self.astrostimer -= self.dt
        if self.astrostimer <= 0 and len(self.astros) < self.nextwave-entity.Astronaut.died:
            self.astrostimer = 2
            self.astros.add(entity.Astronaut(Assets.astronautsprites, self.astroshealth, self.astrosdamage * Sm.app.damagemult))

        # wave, difficulty management
        if entity.Astronaut.died == self.nextwave:
            self.wave += 1
            self.clearedtimer = 0.8
            Assets.clearedsound.play()

            self.boxlimit += 1.4
            self.boxlimit = min(self.boxlimit, 16)
            self.boxtimer = 0.5

            self.astroslimit += 1
            self.astroslimit = min(self.astroslimit, 10)
            self.astrostimer = 3
            self.astroshealth += 6
            self.astrosdamage += 1

            self.nextwave += self.astroslimit

        self.menu.stars()

        self.floorbloodparticles.update()

        #  monster update
        self.monster.update(self.dt)
        tentacleendpos = self.monster.tentacle.endpos.copy()

        self.boxparticles.update()
        for particle in self.boxparticles:
            particle.velocity.y += 120 * self.dt

        #  box update
        tentache_reached = (self.monster.pos - self.monster.tentacle.endpos).length() > self.monster.tentacle.reach * 0.9
        entity.Box.tentacle(self.dt, (tentacleendpos, self.monster.tentacle.endpos), copy.deepcopy(Sm.app.mouse), tentache_reached)
        self.boxes.update()

        #  astronaut update
        self.astros.update()
        self.astrosdeathanim.update('loop')

        # add rocket particles
        self.rocket()

        #  lasers update/draw
        self.lasers.update()
        self.rocketparticles.update()

        self.draw()

        self.bvh = BVH(self.bvh_maxdepth, [self.monster, *self.boxes, *self.astros, *self.lasers])
        #self.bvh.draw(Sm.app.display)
        self.collisions = self.bvh.collisiondict()
        for key in self.collisions:
            key.collision(self.collisions[key])
        self.monster.bvh = self.bvh

        wavetext = ''
        for k, x in enumerate(str(self.wave)):
            wavetext += x+('\n' if k+1 != len(str(self.wave)) else '')

        Assets.font_black.write(wavetext, scale=(2, 2), pos=(1014, 300), relativeOffset=(0.5, 0))
        Assets.font_black.write("W\nA\nV\nE", scale=(1.4, 1.31), pos=(963, 300), relativeOffset=(-0.5, 0))

        if self.asteroidparticles:
            self.asteroidparticles.update()
            for asteroid in self.asteroidparticles:
                asteroid.velocity.y += 350*self.dt

        if self.monster.health <= 0:
            Assets.shade.draw(scale=Sm.app.logical_sizeRect.size, alpha=0.7)
            Assets.font_white.write(f"Wave cleared:\nKills:\nHits taken:\nBoxes thrown:\nTime:", scale=(2, 2), pos=(300, 195))
            Assets.font_white.write(f"{self.wave-1}\n{entity.Astronaut.died}\n{self.monster.hitstaken}\n{entity.Box.thrown}\n{timedelta(seconds=round(self.timer))}", scale=(2, 2), pos=(724, 195), relativeOffset=(0.7, -0.5), align=-1)

            if Sm.app.keys((Sm.app.controls['Ok'], pygame.K_RETURN))[0]:
                Sm.state = "menu"
        else:
            self.timer += self.dt

            if self.clearedtimer > 0:
                self.clearedtimer -= self.dt
                Assets.shade.draw(scale=Sm.app.logical_sizeRect.size, alpha=0.7)
                Assets.font_white.write(f"Wave cleared!", scale=(3, 3), pos=(285, 300), relativeOffset=(-0.5, 0.5))

            self.pausebutton.name = 0
            self.pausebutton.update()
            if Sm.app.keys((Sm.app.controls['Ok'], pygame.K_RETURN))[0] or self.pausebutton.clicked:
                Sm.state = "pause"

        self.exitbutton.update()

        if Sm.app.keys((Sm.app.controls['Esc'],))[0] or self.exitbutton.clicked:
            if self.monster.health <= 0:
                Sm.state = "menu"
            self.monster.health = 0

    def pause(self):

        self.draw()

        wavetext = ''
        for k, x in enumerate(str(self.wave)):
            wavetext += x + ('\n' if k + 1 != len(str(self.wave)) else '')

        Assets.font_black.write(wavetext, scale=(2, 2), pos=(1014, 300), relativeOffset=(0.5, 0))
        Assets.font_black.write("W\nA\nV\nE", scale=(1.4, 1.31), pos=(963, 300), relativeOffset=(-0.5, 0))

        if self.clearedtimer > 0:
            Assets.shade.draw(scale=Sm.app.logical_sizeRect.size, alpha=0.7)
            Assets.font_white.write("Wave cleared!", scale=(3, 3), pos=(285, 300), relativeOffset=(0, 0.5))

        if self.asteroidparticles:
            self.asteroidparticles.update('draw')

        self.pausebutton.name = 1
        self.pausebutton.update()

        if Sm.app.keys((Sm.app.controls['Ok'], Sm.app.controls['Esc'], pygame.K_RETURN))[0] or self.pausebutton.clicked:
            Sm.state = "game"

    def draw(self):
        self.menu.starparticles.update('draw')

        Assets.ship.draw()

        self.floorbloodparticles.update('draw')

        self.boxes.update('shadow')

        self.boxparticles.update('draw')

        monster_y = self.monster.pos.y
        #  astronaut draw1
        for astronaut in sorted(self.astros, key=lambda a: a.pos.y):
            if astronaut.rect.top < monster_y:
                astronaut.update('draw')

        #  astronaut death draw1
        for astronaut in sorted(self.astrosdeathanim, key=lambda a: a.pos.y):
            if astronaut.rect.top < monster_y:
                astronaut.update('draw')

        #  box draw1
        for box in sorted(self.boxes, key=lambda a: a.pos.y):
            if box.pos.y < monster_y:
                box.update('draw')

        #  monster legs draw
        self.monster.legs_draw()

        #  astronaut draw2
        for astronaut in sorted(self.astros, key=lambda a: a.pos.y):
            if astronaut.rect.top >= monster_y:
                astronaut.update('draw')

        #  astronaut death draw2
        for astronaut in sorted(self.astrosdeathanim, key=lambda a: a.pos.y):
            if astronaut.rect.top >= monster_y:
                astronaut.update('draw')

        #  box draw2
        for box in sorted(self.boxes, key=lambda a: a.pos.y):
            if box.pos.y >= monster_y:
                box.update('draw')

        self.drawdoors()

        # body/tentacle draw
        self.monster.tentacle.draw()
        self.monster.body_draw()

        #  lasers update/draw
        self.lasers.update('draw')
        self.laserparticles.update('draw')

        Assets.rocketsprites.draw(0, pos=(28, 208))

    @staticmethod
    def drawdoors():
        k = 0
        for x in ((30, 114), (30, 412), (934, 114), (934, 414)):
            Assets.doorsprites.draw(name=k, pos=x)
            k += 1

    def rocket(self):
        if self.scene.rockettimer <= 0:
            self.scene.rockettimer = random.uniform(0.02, 0.1)

            for fire in ((48, 234, 262), (48, 338, 366), (30, 286, 312)):
                particle = Particle(pos=(fire[0], random.randint(fire[1], fire[2])), sprites=Assets.particlesprites,
                                    animation=(0.3, 14),
                                    velocity=(-140, 0),
                                    scale=(3, 3), rotation=random.randint(-15, 15),
                                    relativeOffset=(-0.5, 0))
                self.rocketparticles.add(particle)
