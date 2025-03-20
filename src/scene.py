import copy
import random

import pygame

import entity
from engine import StateMachine as Sm
from buttons import Button

from assets import Assets
from particles import Particle


class Scene:

    def __init__(self):
        Sm.loadins.append(self.load)
        Sm.states.update({'scene': self.scene,
                          })

    def load(self):
        self.sizehalf = pygame.Vector2(Sm.app.logical_sizeRect.size)/2

    def scene(self):
        if Sm.prevstate != "scene":
            self.scenetimer = 0
            self.rockettimer = 0
            self.laserparticles = pygame.sprite.Group()  # for rocket

            self.boxes = pygame.sprite.Group()
            self.boxparticles = pygame.sprite.Group()
            entity.Box.particles = self.boxparticles

            self.asteroid = [pygame.Vector2(100, -100), -30]

        self.dt = Sm.app.dt

        self.scenetimer += self.dt

        if self.scenetimer >= 1.1 and len(self.boxes) < 3:
            self.boxes.add(entity.Box(Assets.boxsprites, Assets.boxsounds, Assets.boxhitsounds))

        menu = Sm.states["menu_instance"]
        menu.startimer -= self.dt
        menu.stars()
        menu.starparticles.update()

        Assets.ship.draw()

        self.boxes.update('shadow')

        self.boxparticles.update()
        for particle in self.boxparticles:
            particle.velocity.y += 120 * self.dt

        self.boxes.update('draw')
        entity.Box.tentacle(self.dt, ((-100, -100), (100, 100)), copy.deepcopy(Sm.app.mouse), False)
        self.boxes.update()

        Assets.asteroidsprites.draw(0, scale=(2, 2), pos=self.asteroid[0], relativeOffset=(0, 0), rotation=self.asteroid[1])

        reached = self.asteroid[0] != self.sizehalf
        self.asteroid[0].move_towards_ip(self.sizehalf, 500 * self.dt)
        if self.asteroid[0] != self.sizehalf:
            self.asteroid[1] += -290 * self.dt
        if reached and self.asteroid[0] == self.sizehalf:
            Assets.asteroidsound.play()

        self.rockettimer -= self.dt
        self.rocket()
        self.laserparticles.update()

        Assets.rocketsprites.draw(0, pos=(28, 208))

        if self.scenetimer <= 0.3:
            Assets.monstersprites.draw(name=2, scale=(64, 38))
            Assets.font_white.write('! ALERT !', scale=(5, 5), pos=self.sizehalf, relativeOffset=(0, 0.2))

        if self.scenetimer >= 1.6:
            Sm.state = "game"

    def rocket(self):
        if self.rockettimer <= 0:
            self.rockettimer = random.uniform(0.02, 0.1)

            for fire in ((48, 234, 262), (48, 338, 366), (30, 286, 312)):
                particle = Particle(pos=(fire[0], random.randint(fire[1], fire[2])), sprites=Assets.particlesprites,
                                    animation=(0.3, 14),
                                    velocity=(-140, 0),
                                    scale=(3, 3), rotation=random.randint(-15, 15),
                                    relativeOffset=(-0.5, 0))
                self.laserparticles.add(particle)


scene = Scene()
