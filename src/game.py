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
        Sm.states.update(
            {"game": self.game, "pause": self.pause, "game_instance": self}
        )

        self.menu = Sm.states["menu_instance"]
        self.scene = Sm.states["scene_instance"]

        self.boxes = self.scene.boxes
        self.boxParticles = self.scene.boxParticles
        self.laserParticles = self.scene.rocketParticles
        self.timer = 0
        self.clearedTimer = 0
        entity.Astronaut.died = 0
        entity.Box.thrown = 0

        self.move = pygame.Vector2(0, 0)

        self.sizeHalf = pygame.Vector2(Sm.app.logical_sizeRect.size) / 2

        self.pauseButton = Button(
            sprites=Assets.pauseSprites,
            name=0,
            scale=(2, 2),
            pos=(0, 601),
            relativeOffset=(-0.5, 0.5),
            popup=(1.06, 1.06),
        )

        self.exitButton = Button(
            sprites=Assets.buttonSprites,
            name=0,
            scale=(2, 2),
            relativeOffset=(-0.5, -0.5),
            popup=(1.06, 1.06),
        )
        self.exitButton.scale = (2, 2)

        self.monster = Monster(Assets.monsterSprites, Sm.app.monsterScale)
        entity.Astronaut.monster = self.monster

        self.astros = pygame.sprite.Group()
        self.astrosDeathAnim = pygame.sprite.Group()
        entity.Astronaut.deathAnim = self.astrosDeathAnim

        self.lasers = pygame.sprite.Group()
        entity.Laser.group = self.lasers

        self.rocketParticles = self.scene.rocketParticles
        entity.Laser.particles = self.rocketParticles

        self.floorBloodParticles = pygame.sprite.Group()

        self.bvh_max_depth = 5
        self.bvh = BVH(
            self.bvh_max_depth,
            [self.monster, *self.boxes, *self.astros, *self.lasers],
        )
        self.monster.bvh = self.bvh

        self.asteroidParticles = pygame.sprite.Group()
        left = Particle(
            pos=self.sizeHalf,
            sprites=Assets.asteroidSprites,
            animation=(0.6, 1),
            velocity=(-150, -100),
            scale=(2, 2),
            turn=60,
        )
        right = Particle(
            pos=self.sizeHalf,
            sprites=Assets.asteroidSprites,
            animation=(0.6, 2),
            velocity=(150, -100),
            scale=(2, 2),
            turn=-60,
        )
        self.asteroidParticles.add(left, right)

        self.wave = 1
        self.nextWave = 2  # kill requirement

        self.boxLimit = 3
        self.boxTimer = 1

        self.astrosLimit = 2
        self.astrosTimer = 1.5
        self.astrosHealth = 100
        self.astrosDamage = 10

        self.dt = Sm.app.dt
        self.collisions = dict()

    def game(self):
        self.dt = Sm.app.dt

        Sm.states["menu_instance"].starTimer -= self.dt
        Sm.states["scene_instance"].rocketTimer -= self.dt

        if len(self.boxes) < self.boxLimit:
            self.boxTimer -= self.dt
        if self.boxTimer <= 0:
            self.boxTimer = 1
            self.boxes.add(
                entity.Box(
                    Assets.boxSprites, Assets.boxSounds, Assets.boxHitSounds
                )
            )

        self.astrosTimer -= self.dt
        if (
            self.astrosTimer <= 0
            and len(self.astros) < self.nextWave - entity.Astronaut.died
        ):
            self.astrosTimer = 2
            self.astros.add(
                entity.Astronaut(
                    Assets.astronautSprites,
                    self.astrosHealth,
                    self.astrosDamage * Sm.app.damageMult,
                )
            )

        # wave, difficulty management
        if entity.Astronaut.died == self.nextWave:
            self.wave += 1
            self.clearedTimer = 0.8
            Assets.clearedSound.play()

            self.boxLimit += 1.4
            self.boxLimit = min(self.boxLimit, 16)
            self.boxTimer = 0.5

            self.astrosLimit += 1
            self.astrosLimit = min(self.astrosLimit, 10)
            self.astrosTimer = 3
            self.astrosHealth += 6
            self.astrosDamage += 1

            self.nextWave += self.astrosLimit

        self.menu.stars()

        self.floorBloodParticles.update()

        #  monster update
        self.monster.update(self.dt)
        tentacle_end_pos = self.monster.tentacle.endPos.copy()

        self.boxParticles.update()
        for particle in self.boxParticles:
            particle.velocity.y += 120 * self.dt

        #  box update
        tentacle_reached = (
            self.monster.pos - self.monster.tentacle.endPos
        ).length() > self.monster.tentacle.reach * 0.9
        entity.Box.tentacle(
            self.dt,
            (tentacle_end_pos, self.monster.tentacle.endPos),
            copy.deepcopy(Sm.app.mouse),
            tentacle_reached,
        )
        self.boxes.update()

        #  astronaut update
        self.astros.update()
        self.astrosDeathAnim.update("loop")

        # add rocket particles
        self.rocket()

        #  lasers update/draw
        self.lasers.update()
        self.rocketParticles.update()

        #  draw game layers
        self.draw()

        self.bvh = BVH(
            self.bvh_max_depth,
            [self.monster, *self.boxes, *self.astros, *self.lasers],
        )
        #  debug BVH
        # self.bvh.draw(Sm.app.display)
        self.collisions = self.bvh.collisionDict()
        for key in self.collisions:
            key.collision(self.collisions[key])
        self.monster.bvh = self.bvh

        if self.asteroidParticles:
            self.asteroidParticles.update()
            for asteroid in self.asteroidParticles:
                asteroid.velocity.y += 350 * self.dt

        # game over
        if self.monster.health <= 0:
            Assets.shade.draw(scale=Sm.app.logical_sizeRect.size, alpha=0.7)
            Assets.font_white.write(
                "Wave cleared:\nKills:\nHits taken:\nBoxes thrown:\nTime:",
                scale=(2, 2),
                pos=(300, 195),
            )
            Assets.font_white.write(
                f"{self.wave-1}\n"
                f"{entity.Astronaut.died}\n"
                f"{self.monster.hitsTaken}\n"
                f"{entity.Box.thrown}\n"
                f"{timedelta(seconds=round(self.timer))}",
                scale=(2, 2),
                pos=(724, 195),
                relativeOffset=(0.7, -0.5),
                align=-1,
            )

            if Sm.app.keys((Sm.app.controls["Ok"], pygame.K_RETURN))[0]:
                Sm.state = "menu"
        else:
            self.timer += self.dt

            if self.clearedTimer > 0:
                self.clearedTimer -= self.dt
                Assets.shade.draw(
                    scale=Sm.app.logical_sizeRect.size, alpha=0.7
                )
                Assets.font_white.write(
                    "Wave cleared!",
                    scale=(3, 3),
                    pos=(285, 300),
                    relativeOffset=(-0.5, 0.5),
                )

            self.pauseButton.name = 0
            self.pauseButton.update()
            if (
                Sm.app.keys((Sm.app.controls["Ok"], pygame.K_RETURN))[0]
                or self.pauseButton.clicked
            ):
                Sm.state = "pause"

        self.exitButton.update()

        if (
            Sm.app.keys((Sm.app.controls["Esc"],))[0]
            or self.exitButton.clicked
        ):
            if self.monster.health <= 0:
                Sm.state = "menu"
            self.monster.health = 0

    def pause(self):

        self.draw()

        if self.clearedTimer > 0:
            Assets.shade.draw(scale=Sm.app.logical_sizeRect.size, alpha=0.7)
            Assets.font_white.write(
                "Wave cleared!",
                scale=(3, 3),
                pos=(285, 300),
                relativeOffset=(0, 0.5),
            )

        if self.asteroidParticles:
            self.asteroidParticles.update("draw")

        self.pauseButton.name = 1
        self.pauseButton.update()

        if (
            Sm.app.keys(
                (
                    Sm.app.controls["Ok"],
                    Sm.app.controls["Esc"],
                    pygame.K_RETURN,
                )
            )[0]
            or self.pauseButton.clicked
        ):
            Sm.state = "game"

    def draw(self):
        self.menu.starParticles.update("draw")

        Assets.ship.draw()

        self.floorBloodParticles.update("draw")

        self.boxes.update("shadow")

        self.boxParticles.update("draw")

        monster_y = self.monster.pos.y
        #  astronaut draw1
        for astronaut in sorted(self.astros, key=lambda a: a.pos.y):
            if astronaut.rect.top < monster_y:
                astronaut.update("draw")

        #  astronaut death draw1
        for astronaut in sorted(self.astrosDeathAnim, key=lambda a: a.pos.y):
            if astronaut.rect.top < monster_y:
                astronaut.update("draw")

        #  box draw1
        for box in sorted(self.boxes, key=lambda a: a.pos.y):
            if box.pos.y < monster_y:
                box.update("draw")

        #  monster legs draw
        self.monster.legs_draw()

        #  astronaut draw2
        for astronaut in sorted(self.astros, key=lambda a: a.pos.y):
            if astronaut.rect.top >= monster_y:
                astronaut.update("draw")

        #  astronaut death draw2
        for astronaut in sorted(self.astrosDeathAnim, key=lambda a: a.pos.y):
            if astronaut.rect.top >= monster_y:
                astronaut.update("draw")

        #  box draw2
        for box in sorted(self.boxes, key=lambda a: a.pos.y):
            if box.pos.y >= monster_y:
                box.update("draw")

        self.drawDoors()

        # body/tentacle draw
        self.monster.tentacle.draw()
        self.monster.body_draw()

        #  lasers update/draw
        self.lasers.update("draw")
        self.laserParticles.update("draw")

        Assets.rocketSprites.draw(0, pos=(28, 208))

        wave_text = ""
        for k, x in enumerate(str(self.wave)):
            wave_text += x + ("\n" if k + 1 != len(str(self.wave)) else "")

        Assets.font_black.write(
            wave_text, scale=(2, 2), pos=(1014, 300), relativeOffset=(0.5, 0)
        )
        Assets.font_black.write(
            "W\nA\nV\nE",
            scale=(1.4, 1.31),
            pos=(963, 300),
            relativeOffset=(-0.5, 0),
        )

    @staticmethod
    def drawDoors():
        k = 0
        for x in ((30, 114), (30, 412), (934, 114), (934, 414)):
            Assets.doorSprites.draw(name=k, pos=x)
            k += 1

    def rocket(self):
        if self.scene.rocketTimer <= 0:
            self.scene.rocketTimer = random.uniform(0.02, 0.1)

            for fire in ((48, 234, 262), (48, 338, 366), (30, 286, 312)):
                particle = Particle(
                    pos=(fire[0], random.randint(fire[1], fire[2])),
                    sprites=Assets.particleSprites,
                    animation=(0.3, 14),
                    velocity=(-140, 0),
                    scale=(3, 3),
                    rotation=random.randint(-15, 15),
                    relativeOffset=(-0.5, 0),
                )
                self.rocketParticles.add(particle)
