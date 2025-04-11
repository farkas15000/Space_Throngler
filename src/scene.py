import copy
import random

import pygame

import entity
from engine import StateMachine as Sm
from assets import Assets
from particles import Particle
from game import Game


class Scene:
    """Short animated intro scene after game start"""

    def __init__(self):

        Sm.loadIns.append(self.load)
        Sm.states.update({'scene': self.scene,
                          'scene_instance': self
                          })

        self.sceneTimer = 0
        self.rocketTimer = 0
        self.rocketParticles = pygame.sprite.Group()

        self.boxes = pygame.sprite.Group()
        self.boxParticles = pygame.sprite.Group()

        self.dt = 0
        self.asteroid = None
        self.sizeHalf = None

    def load(self):
        self.sizeHalf = pygame.Vector2(Sm.app.logical_sizeRect.size) / 2

    def scene(self):
        if Sm.prevState != "scene":
            self.sceneTimer = 0
            self.rocketTimer = 0
            self.rocketParticles = pygame.sprite.Group()

            self.boxes = pygame.sprite.Group()
            self.boxParticles = pygame.sprite.Group()
            entity.Box.particles = self.boxParticles

            self.asteroid = [pygame.Vector2(100, -100), -30]

        self.dt = Sm.app.dt

        self.sceneTimer += self.dt

        if self.sceneTimer >= 1.1 and len(self.boxes) < 3:
            self.boxes.add(entity.Box(Assets.boxSprites, Assets.boxSounds, Assets.boxHitSounds))

        menu = Sm.states["menu_instance"]
        menu.starTimer -= self.dt
        menu.stars()
        menu.starParticles.update()

        Assets.ship.draw()

        self.boxes.update('shadow')

        self.boxParticles.update()
        for particle in self.boxParticles:
            particle.velocity.y += 120 * self.dt

        self.boxes.update('draw')
        entity.Box.tentacle(self.dt, ((-100, -100), (100, 100)), copy.deepcopy(Sm.app.mouse), False)
        self.boxes.update()

        Assets.asteroidSprites.draw(0, scale=(2, 2), pos=self.asteroid[0], relativeOffset=(0, 0), rotation=self.asteroid[1])

        reached = self.asteroid[0] != self.sizeHalf
        self.asteroid[0].move_towards_ip(self.sizeHalf, 500 * self.dt)
        if self.asteroid[0] != self.sizeHalf:
            self.asteroid[1] += -290 * self.dt
        if reached and self.asteroid[0] == self.sizeHalf:
            Assets.asteroidSound.play()

        self.rocketTimer -= self.dt
        self.rocket()
        self.rocketParticles.update()

        Assets.rocketSprites.draw(0, pos=(28, 208))

        if self.sceneTimer <= 0.3:
            Assets.monsterSprites.draw(name=2, scale=(64, 38))
            Assets.font_white.write('! ALERT !', scale=(5, 5), pos=self.sizeHalf, relativeOffset=(0, 0.2))

        if self.sceneTimer >= 1.6:
            Game()

    def rocket(self):
        if self.rocketTimer <= 0:
            self.rocketTimer = random.uniform(0.02, 0.1)

            for fire in ((48, 234, 262), (48, 338, 366), (30, 286, 312)):
                particle = Particle(pos=(fire[0], random.randint(fire[1], fire[2])), sprites=Assets.particleSprites,
                                    animation=(0.3, 14),
                                    velocity=(-140, 0),
                                    scale=(3, 3), rotation=random.randint(-15, 15),
                                    relativeOffset=(-0.5, 0))
                self.rocketParticles.add(particle)
