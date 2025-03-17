"""
To enable debug mode go to line 712 and 716.
"""

import asyncio
import platform
from datetime import timedelta
import pygame
import sys
import time
import random
import os
import copy
from pygame._sdl2.video import Window, Renderer, Texture
if sys.platform == "emscripten":
    platform.window.canvas.style.imageRendering = "pixelated"

from engine import StateMachine as Sm
from buttons import Button
from multi_sprite_renderer_hardware import MultiSprite as Msr
from assets import Assets
from particles import Particle
from monster import Monster
import entity
from BVH import BVH
print('_SDL2 rendering')



def map_value(value, valuemin, valuemax, mapmin, mapmax):
    return ((value - valuemin) / (valuemax - valuemin)) * (mapmax - mapmin) + mapmin


def sprite_slicer(width, height, wpad=0, hpad=0, outputlist=None, folders=(), name='', sprite=None):
    # cuts up image from file or Surface with optional padding and output list

    if width <= 0 or height <= 0:
        raise Exception('need area!')

    if sprite is None:
        img = pygame.image.load(os.path.join(*folders, name + '.png')).convert_alpha()
    else:
        img = sprite
    imgh = img.get_height()
    col = 0
    if outputlist is None:
        outputlist = []

    while imgh // height > 0:
        imgw = img.get_width()
        row = 0
        while imgw//width > 0:
            imgw -= width+wpad
            sprite = img.subsurface(pygame.Rect(row * (width+wpad), col * (height+hpad), width, height))
            outputlist.append(sprite)
            row += 1

        imgh -= height + hpad
        col += 1

    return outputlist


class App:

    def __init__(self):
        self.winresolution = 1024, 600
        self.fullscreen = False

        self.soundvolume = 0.5

        self.damagemult = 1

        self.controls = {'Up': pygame.K_w,
                         'Down': pygame.K_s,
                         'Left': pygame.K_a,
                         'Right': pygame.K_d,
                         'Ok': pygame.K_SPACE,
                         'Esc': pygame.K_ESCAPE,
                         }

        abspath = os.path.dirname(os.path.abspath(__file__))
        self.spritespath = os.path.join(abspath, 'assets', 'sprites')
        self.audiopath = os.path.join(abspath, 'assets', 'audio')
        self.fontpath = os.path.join(abspath, 'assets', 'fonts')

        if hasattr(platform, 'window'):
            self.mobile = platform.window.mobile_check() or platform.window.mobile_tablet()
        else:
            self.mobile = False

        pygame.init()
        self.clock = pygame.time.Clock()

        self.logical_sizeRect = pygame.Rect(0, 0, 1024, 600)

        self.window = Window(size=(1024, 600))
        self.window.resizable = True
        self.window.title = "Space Throngler!"

        self.display = Renderer(self.window, accelerated=-1, target_texture=False)
        self.screen = Texture(self.display, self.logical_sizeRect.size, target=True)
        Msr.setScreen(self.display)

        self.states = {'menu': self.menu,
                       'game': self.game,
                       'scene': self.scene,
                       'pause': self.pause,
                       'loadin': self.loadin,
                       }

        self.dt = 0.016
        self.running = True

        Button.controls = self.controls

        Assets.makemsrs()
        Assets.makeaudio()

        Sm.app = self
        Sm.state = 'menu'
        Sm.states['game'] = None

    def menu(self):
        if self.stateprev[0] != self.stateloop:
            #print('menu')
            self.startimer = 0
            self.menustartimer = 0
            self.trailtimer = 0
            self.asteroidrot = 23

            self.exitbutton.scale = (3, 3)

        self.startimer -= self.dt
        self.stars()

        self.menustartimer -= self.dt
        if self.menustartimer <= 0:
            self.menustartimer = random.uniform(0.2, 0.5)
            self.menustarsadd()
        self.menustars.update()


        self.trailtimer -= self.dt
        if self.trailtimer <= 0:
            self.trailtimer = random.uniform(0.05, 0.1)
            for z in range(5):
                rot = random.randint(160, 200)
                trail = Particle(pos=(880+random.randint(-20, 20), 305+random.randint(-40, 40)), sprites=self.particlesprites,
                                 animation=(random.uniform(0.3, 0.45), 4),
                                 velocity=pygame.Vector2(random.randint(280, 320), 0).rotate(-rot),
                                 scale=(4, 4), rotation=rot+180)
                self.menustars.add(trail)

        self.asteroidrot -= 45 * self.dt
        asteroid = self.asteroidsprites.draw(0, scale=(3, 3), pos=(880, 305), offset=(0, 0), rotation=self.asteroidrot)[0]
        if self.mouseclicked and self.easteregg < 10 and asteroid.collidepoint(self.mousepos[1]):
            self.easteregg += 1
            self.clearedsound.play()

        if self.easteregg >= 10:
            self.eastereggsprite.draw(0, scale=(2, 2), pos=(120, 235))
            self.soundsprites.draw(2, scale=(1, 1), pos=(60, 370), offset=(-0.5, 0))
            self.eastereggknob.update()
            if self.eastereggknob.grabbed:
                posx = self.eastereggknob.pos.x
                self.eastereggknob.pos.x = pygame.math.clamp(self.mousepos[1][0], 84, 234)
                if posx != self.eastereggknob.pos.x:
                    self.scale = round(map_value(self.eastereggknob.pos.x, 84, 234, 0.5, 4), 1)
            self.font_white.write(f'Size:{round(self.scale, 1)}x', scale=(2, 2), pos=(52, 400))

        self.text_menu.draw(0, scale=(3, 3), pos=(512, 150), offset=(0, 0))
        self.text_menu.draw(1, scale=(2, 2), pos=(512, 480), offset=(0, 0))
        self.text_menu.draw(2, scale=(2, 2), pos=(512, 540), offset=(0, 0))

        eyepos = pygame.Vector2(599, 151)
        offset = -eyepos + self.mousepos[1]
        if offset:
            offset = offset.normalize() * 3
        offset.x *= 1.4
        self.monstersprites.draw(name=1, scale=(1.6, 1.6), pos=eyepos+offset, offset=(0, 0))

        self.exitbutton.update()
        self.startbutton.update()

        self.soundsprites.draw(0, scale=(1.6, 1.6), pos=(475, 370), offset=(0.5, 0))
        self.soundsprites.draw(2, scale=(1, 1), pos=(507, 370), offset=(-0.5, 0))

        self.soundbutton.update()
        if self.soundbutton.grabbed:
            posx = self.soundbutton.pos.x
            self.soundbutton.pos.x = pygame.math.clamp(self.mousepos[1][0], 531, 681)
            if posx != self.soundbutton.pos.x:
                self.soundvolume = map_value(self.soundbutton.pos.x, 531, 681, 0, 1)
                self.audio()
        if self.keys((self.controls['Left'], pygame.K_LEFT, self.controls['Down'], pygame.K_DOWN))[0]:
            self.soundvolume -= 0.05
            self.soundvolume = max(self.soundvolume, 0)
            self.audio()
            self.soundbutton.pos.x = map_value(self.soundvolume, 0, 1, 531, 681)
        if self.keys((self.controls['Right'], pygame.K_RIGHT, self.controls['Up'], pygame.K_UP))[0]:
            self.soundvolume += 0.05
            self.soundvolume = min(self.soundvolume, 1)
            self.audio()
            self.soundbutton.pos.x = map_value(self.soundvolume, 0, 1, 531, 681)

        self.mobilebutton.update()
        if self.mobilebutton.clicked:
            self.mobile = not self.mobile
            self.mobilebutton.name = self.mobile

        if self.keys((self.controls['Esc'],))[0] or self.exitbutton.clicked:
            pygame.quit()
            exit()

        if self.keys((self.controls['Ok'], pygame.K_RETURN))[0] or self.startbutton.clicked:
            self.stateloop = self.states['scene']

    def scene(self):
        if self.stateprev[0] != self.stateloop:
            self.scenetimer = 0
            self.rockettimer = 0
            self.laserparticles = pygame.sprite.Group()  # for rocket

            self.boxes = pygame.sprite.Group()
            self.boxparticles = pygame.sprite.Group()
            entity.Box.particles = self.boxparticles

            self.asteroid = [pygame.Vector2(100, -100), -30]

        self.scenetimer += self.dt

        if self.scenetimer >= 1.1 and len(self.boxes) < 3:
            self.boxes.add(entity.Box(self.boxsprites, self.boxsounds, self.boxhitsounds))

        self.startimer -= self.dt
        self.stars()
        self.starparticles.update()

        self.ship.draw()

        self.boxes.update('shadow')

        self.boxparticles.update()
        for particle in self.boxparticles:
            particle.velocity.y += 120 * self.dt

        self.boxes.update('draw')
        entity.Box.tentacle(self.dt, ((-100, -100), (100, 100)), copy.deepcopy(self.mouse), False)
        self.boxes.update()

        self.asteroidsprites.draw(0, scale=(2, 2), pos=self.asteroid[0], offset=(0, 0), rotation=self.asteroid[1])
        reached = self.asteroid[0]!=(self.width / 2, self.height / 2)
        self.asteroid[0].move_towards_ip((self.width / 2, self.height / 2), 500 * self.dt)
        if self.asteroid[0] != (self.width / 2, self.height / 2):
            self.asteroid[1] += -290 * self.dt
        if reached and self.asteroid[0]==(self.width / 2, self.height / 2):
            self.asteroidsound.play()

        self.rockettimer -= self.dt
        self.rocket()
        self.laserparticles.update()

        self.rocketsprites.draw(0, pos=(28, 208))

        if self.scenetimer <= 0.3:
            self.monstersprites.draw(name=2, scale=(64, 38))
            self.font_white.write('! ALERT !', scale=(5, 5), pos=(240, 300), offset=(0, 0.5))

        if self.scenetimer >= 1.6:
            self.stateloop = self.states['game']

    def game(self):
        if self.stateprev[0] != self.stateloop and self.stateprev[0] != self.states['pause']:
            #print('game')

            # setup/reset stuff
            self.timer = 0
            self.clearedtimer = 0
            entity.Astronaut.died = 0
            entity.Box.thrown = 0

            self.exitbutton.scale = (2, 2)

            self.monster = Monster(self, self.monstersprites, self.scale)
            entity.Astronaut.monster = self.monster

            self.astros = pygame.sprite.Group()
            self.astrosdeathanim = pygame.sprite.Group()
            entity.Astronaut.deathanim = self.astrosdeathanim

            self.lasers = pygame.sprite.Group()
            entity.Laser.group = self.lasers

            entity.Laser.particles = self.laserparticles

            self.floorbloodparticles = pygame.sprite.Group()

            self.bvh_maxdepth = 5
            self.bvh = BVH(self.bvh_maxdepth, [self.monster, *self.boxes, *self.astros, *self.lasers])
            self.monster.bvh = self.bvh

            self.asteroidparticles = pygame.sprite.Group()
            left = Particle(pos=(self.width/2, self.height/2), sprites=self.asteroidsprites,
                                animation=(0.6, 1),
                                velocity=(-150, -100),
                                scale=(2, 2), turn=60)
            right = Particle(pos=(self.width / 2, self.height / 2), sprites=self.asteroidsprites,
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

        self.startimer -= self.dt
        self.rockettimer -= self.dt

        if len(self.boxes) < self.boxlimit:
            self.boxtimer -= self.dt
        if self.boxtimer <= 0:
            self.boxtimer = 1
            self.boxes.add(entity.Box(self.boxsprites, self.boxsounds, self.boxhitsounds))

        self.astrostimer -= self.dt
        if self.astrostimer <= 0 and len(self.astros) < self.nextwave-entity.Astronaut.died:
            self.astrostimer = 2
            self.astros.add(entity.Astronaut(self.astronautsprites, self.astroshealth, self.astrosdamage*self.damagemult))

        # wave, difficulty management
        if entity.Astronaut.died == self.nextwave:
            self.wave += 1
            self.clearedtimer = 0.8
            self.clearedsound.play()

            self.boxlimit += 1.4
            self.boxlimit = min(self.boxlimit, 16)
            self.boxtimer = 0.5

            self.astroslimit += 1
            self.astroslimit = min(self.astroslimit, 10)
            self.astrostimer = 3
            self.astroshealth += 6
            self.astrosdamage += 1

            self.nextwave += self.astroslimit

        self.stars()
        self.starparticles.update('draw')

        self.ship.draw()

        self.floorbloodparticles.update()

        self.boxes.update('shadow')

        if self.mobile:
            if self.monster.pos.distance_squared_to(self.mousepos[1]) > (192/2.5*0.6875)**2:
                vect = self.monster.pos - self.mousepos[1]
                if vect.x != 0 or vect.y != 0:
                    vect = vect.normalize()
                    vect *= -1
                self.move = vect
            else:
                self.move.update(0, 0)

        #  monster update
        self.monster.update(self.dt, self.move, self.mousepos[1])
        tentacleendpos = self.monster.tentacle.endpos.copy()

        self.boxparticles.update()
        for particle in self.boxparticles:
            particle.velocity.y += 120 * self.dt

        #  box update
        tentache_reached = (self.monster.pos - self.monster.tentacle.endpos).length() > self.monster.tentacle.reach * 0.9
        entity.Box.tentacle(self.dt, (tentacleendpos, self.monster.tentacle.endpos), copy.deepcopy(self.mouse), tentache_reached)
        self.boxes.update()

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

        #  monster tentacle, legs draw
        self.monster.legs_draw()
        self.monster.tentacle.draw()

        #  astronaut draw2
        for astronaut in sorted(self.astros, key=lambda a: a.pos.y):
            if astronaut.rect.top >= monster_y:
                astronaut.update('draw')

        #  astronaut death draw2
        for astronaut in sorted(self.astrosdeathanim, key=lambda a: a.pos.y):
            if astronaut.rect.top >= monster_y:
                astronaut.update('draw')

        self.astrosdeathanim.update('loop')

        #  box draw2
        for box in sorted(self.boxes, key=lambda a: a.pos.y):
            if box.pos.y >= monster_y:
                box.update('draw')

        self.drawdoors()

        # body/tentacle draw
        self.monster.tentacle.draw()
        self.monster.body_draw()

        #  astronaut update
        self.astros.update()

        # add rocket particles
        self.rocket()

        #  lasers update/draw
        self.lasers.update()
        self.laserparticles.update()

        self.rocketsprites.draw(0, pos=(28, 208))

        self.bvh = BVH(self.bvh_maxdepth, [self.monster, *self.boxes, *self.astros, *self.lasers])  # BVH creation per frame
        #self.bvh.draw(self.window)                                             # debug, draws full bvh tree (note 1)
        self.collisions = self.bvh.collisiondict()
        #print(self.collisions)
        self.collisionshandle()
        self.monster.bvh = self.bvh

        wavetext = ''
        for k, x in enumerate(str(self.wave)):
            wavetext += x+('\n' if k+1 != len(str(self.wave)) else '')

        self.font_black.write(wavetext, scale=(2, 2), pos=(1014, 300), offset=(1, 0.5))
        self.font_black.write("W\nA\nV\nE", scale=(1.4, 1.31), pos=(963, 300), offset=(0, 0.5))

        if self.asteroidparticles:
            self.asteroidparticles.update()
            for asteroid in self.asteroidparticles:
                asteroid.velocity.y += 350*self.dt

        if self.monster.health <= 0:
            self.shade.draw()
            self.font_white.write(f"Wave cleared:\nKills:\nHits taken:\nBoxes thrown:\nTime:", scale=(2, 2), pos=(300, 195))
            self.font_white.write(f"{self.wave-1}\n{entity.Astronaut.died}\n{self.monster.hitstaken}\n{entity.Box.thrown}\n{timedelta(seconds=round(self.timer))}", scale=(2, 2), pos=(724, 195), offset=(True, 0))

            if self.keys((self.controls['Ok'], pygame.K_RETURN))[0]:
                self.stateloop = self.states['menu']
        else:
            self.timer += self.dt

            if self.clearedtimer > 0:
                self.clearedtimer -= self.dt
                self.shade.draw()
                self.font_white.write(f"Wave cleared!", scale=(3, 3), pos=(285, 300), offset=(0, 0.5))

            self.pausebutton.name = 0
            self.pausebutton.update()
            if self.keys((self.controls['Ok'], pygame.K_RETURN))[0] or self.pausebutton.clicked:
                self.stateloop = self.states['pause']

        self.exitbutton.update()

        if self.keys((self.controls['Esc'],))[0] or self.exitbutton.clicked:
            if self.monster.health <= 0:
                self.stateloop = self.states['menu']
            self.monster.health = 0

    def pause(self):
        if self.stateprev[0] != self.stateloop:
            #print('pause')
            pass

        self.starparticles.update('draw')

        self.ship.draw()

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

        #  monster draw
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

        self.rocketsprites.draw(0, pos=(28, 208))

        wavetext = ''
        for k, x in enumerate(str(self.wave)):
            wavetext += x + ('\n' if k + 1 != len(str(self.wave)) else '')

        self.font_black.write(wavetext, scale=(2, 2), pos=(1014, 300), offset=(1, 0.5))
        self.font_black.write("W\nA\nV\nE", scale=(1.4, 1.31), pos=(963, 300), offset=(0, 0.5))

        if self.clearedtimer > 0:
            self.shade.draw()
            self.font_white.write("Wave cleared!", scale=(3, 3), pos=(285, 300), offset=(0, 0.5))

        if self.asteroidparticles:
            self.asteroidparticles.update('draw')

        self.pausebutton.name = 1
        self.pausebutton.update()

        if self.keys((self.controls['Ok'], self.controls['Esc'], pygame.K_RETURN))[0] or self.pausebutton.clicked:
            self.stateloop = self.states['game']

    def collisionshandle(self):
        for key in self.collisions:
            key.collision(self.collisions[key])

    def drawdoors(self):
        k = 0
        for x in ((30, 114), (30, 412), (934, 114), (934, 414)):
            self.doorsprites.draw(name=k, pos=x)
            k += 1

    def stars(self):
        self.starparticles.update('loop')
        if self.startimer <= 0:
            self.startimer = random.uniform(0.8, 1)
            speedrange = (40, 60)

            for star in ((1040, 15, 25, 1040, 42, 180), (1040, 575, 585, 1040, 420, 558), (446, 15, 25, 40, 42, 190), (446, 575, 585, 40, 410, 558)):
                speed = random.randint(*speedrange)
                particle = Particle(pos=(star[0], random.randint(star[1], star[2])), sprites=Particle.sprites,
                                    animation=(460 / speed, 1 + random.randrange(3)),
                                    velocity=(-speed, 0),
                                    scale=(2, 2), rotation=random.randrange(10) * 36 + 6,
                                    offset=(random.uniform(-1, 1), random.uniform(-1, 1)))
                self.starparticles.add(particle)

                for z in range(2):
                    speed = random.randint(*speedrange)
                    particle = Particle(pos=(star[3], random.randint(star[4], star[5])), sprites=Particle.sprites,
                                        animation=(55/speed, 1+random.randrange(3)),
                                        velocity=(-speed, 0),
                                        scale=(2, 2), rotation=random.randrange(10) * 36+15,
                                        offset=(random.uniform(-1, 1), random.uniform(-1, 1)))
                    self.starparticles.add(particle)

            #print(len(self.starparticles))

    def menustarsadd(self, preload=False):

        speed = random.randint(40, 60)
        particle = Particle(pos=(random.randint(15, 1009) if preload else 1040, random.randint(5, 595)), sprites=Particle.sprites,
                            animation=(1080 / speed, 1 + random.randrange(3)),
                            velocity=(-speed, 0),
                            scale=(2, 2), rotation=random.randrange(10) * 36 + 15,
                            offset=(random.uniform(-1, 1), random.uniform(-1, 1)))
        self.menustars.add(particle)


    def rocket(self):
        if self.rockettimer <= 0:
            self.rockettimer = random.uniform(0.02, 0.1)

            for fire in ((48, 234, 262), (48, 338, 366), (30, 286, 312)):
                particle = Particle(pos=(fire[0], random.randint(fire[1], fire[2])), sprites=Particle.sprites,
                                    animation=(0.3, 14),
                                    velocity=(-140, 0),
                                    scale=(3, 3), rotation=random.randint(-15, 15),
                                    offset=(-0.5, 0))
                self.laserparticles.add(particle)

    def loadin(self):
        # load in all assets, set sound volume

        #print('loadin')
        self.stateloop = self.states['menu']

        linkedsprites = []

        self.font_black = Msr(self.window, folders=(self.fontpath,), font='VCR_OSD_MONO_1.001', size=21, color='Black')
        self.font_white = Msr(self.window, folders=(self.fontpath,), font='VCR_OSD_MONO_1.001', size=21)

        ship = pygame.image.load(os.path.join(self.spritespath, 'ship5' + '.png')).convert()
        ship.set_colorkey((163, 73, 164))
        ship.fill((234, 234, 234, 0), (50, 18, 412, 264))
        ship = pygame.transform.scale_by(ship, 2)
        self.ship = Msr(self.window, images=(ship,), alpha=1)

        shade = pygame.Surface((1024, 600))
        self.shade = Msr(self.window, images=(shade,), alpha=0.7)

        doors = pygame.image.load(os.path.join(self.spritespath, 'doors1' + '.png')).convert()
        doors.set_colorkey((163, 73, 164))
        doors = pygame.transform.scale_by(doors, 2)
        linkedsprites.clear()
        sprite_slicer(30*2, 36*2, wpad=2*2, outputlist=linkedsprites, sprite=doors)
        self.doorsprites = Msr(self.window, images=linkedsprites)

        rocket = pygame.image.load(os.path.join(self.spritespath, 'rocket' + '.png')).convert()
        rocket.set_colorkey((163, 73, 164))
        rocket = pygame.transform.scale_by(rocket, 2)
        self.rocketsprites = Msr(self.window, images=(rocket,))

        self.scale = 1.0
        healthbox = pygame.Surface((32, 8))
        healthbox.fill((255, 255, 255, 0), (1, 1, 30, 6))
        health = pygame.Surface((32, 8))
        health.fill((163, 73, 164))
        health.set_colorkey((163, 73, 164))
        health.fill((138, 15, 52), (1, 1, 30, 6))
        self.monstersprites = Msr(self.window, folders=(self.spritespath,), names=("head", "eye", "limb", "joint"), images=(healthbox, health))

        linkedsprites.clear()
        sprite_slicer(22, 22, outputlist=linkedsprites, folders=(self.spritespath,), name='box_sprites1')
        boxoutline = pygame.image.load(os.path.join(self.spritespath, 'boxoutline' + '.png')).convert()
        boxoutline.set_colorkey((163, 73, 164))
        linkedsprites.append(boxoutline)
        sprite_slicer(22, 22, outputlist=linkedsprites, folders=(self.spritespath,), name='box_shadow_sprites')
        self.boxsprites = Msr(self.window, images=linkedsprites)

        linkedsprites.clear()
        sprite_slicer(24, 24, outputlist=linkedsprites, folders=(self.spritespath,), name='astronaut_walk_sprites1')
        sprite_slicer(24, 24, outputlist=linkedsprites, folders=(self.spritespath,), name='astronaut_die_sprites1')
        self.astronautsprites = Msr(self.window, images=linkedsprites)

        self.lasersprites = Msr(self.window, folders=(self.spritespath,), names=("laser1",))
        self.lasersprites.windowrect = pygame.rect.Rect(102, 32, 820, 532)
        entity.Laser.sprites = self.lasersprites

        linkedsprites.clear()
        sprite_slicer(6, 6, wpad=1, hpad=1, outputlist=linkedsprites, folders=(self.spritespath,), name='blood1')
        self.bloodsprites = Msr(self.window, images=linkedsprites)
        self.lasersprites.windowrect = pygame.rect.Rect(102, 32, 820, 532)
        entity.Astronaut.bloodsprites = self.bloodsprites

        particles = pygame.image.load(os.path.join(self.spritespath, 'particles1' + '.png')).convert()
        particles.set_colorkey((163, 73, 164))
        linkedsprites.clear()
        sprite_slicer(7, 7, wpad=1, hpad=1, outputlist=linkedsprites, sprite=particles)
        self.particlesprites = Msr(self.window, images=linkedsprites)
        Particle.sprites = self.particlesprites

        self.starparticles = pygame.sprite.Group()

        exitB = pygame.image.load(os.path.join(self.spritespath, 'exit' + '.png')).convert()
        exitB.set_colorkey((163, 73, 164))
        self.buttonsprites = Msr(self.window, images=(exitB,))
        self.exitbutton = Button(sprites=self.buttonsprites, name=0, scale=(2, 2), offset=(-0.5, -0.5), popup=(1.06, 1.06))

        linkedsprites.clear()
        pauseB = pygame.image.load(os.path.join(self.spritespath, 'pause' + '.png')).convert()
        pauseB.set_colorkey((163, 73, 164))
        sprite_slicer(38, 20, outputlist=linkedsprites, sprite=pauseB)
        self.pausesprites = Msr(self.window, images=linkedsprites)
        self.pausebutton = Button(sprites=self.pausesprites, name=0, scale=(2, 2), pos=(0, 601), offset=(-0.5, 0.5), popup=(1.06, 1.06))

        self.startsprites = Msr(self.window, folders=(self.spritespath,), names=('start1',))
        self.startbutton = Button(sprites=self.startsprites, name=0, scale=(2, 2), pos=(512, 270),  offset=(0, 0), popup=(1.04, 1.04))

        soundbar = pygame.Surface((198, 16))
        soundbar.fill((255, 255, 255, 0))
        self.soundsprites = Msr(self.window, folders=(self.spritespath,), names=('sound', 'sound knob'), images=(soundbar,))
        self.soundbutton = Button(sprites=self.soundsprites, name=1, scale=(3, 3), pos=pygame.Vector2(map_value(self.soundvolume, 0, 1, 531, 681), 370), offset=(0, 0), popup=(1.04, 1.04))

        self.easteregg = False
        self.eastereggsprite = Msr(self.window, folders=(self.spritespath,), names=("easter egg",))
        self.eastereggknob = Button(sprites=self.soundsprites, name=1, scale=(3, 3), pos=pygame.Vector2(map_value(self.scale, 0.5, 4, 84, 234), 370), offset=(0, 0), popup=(1.04, 1.04))

        linkedsprites.clear()
        sprite_slicer(144, 32, outputlist=linkedsprites, folders=(self.spritespath,), name='mobile_sprites1')
        self.mobilesprites = Msr(self.window, images=linkedsprites)
        self.mobilebutton = Button(sprites=self.mobilesprites, name=self.mobile, scale=(2, 2), pos=(1014, 12), offset=(0.5, -0.5), popup=(1, 1))

        self.text_menu = Msr(self.window, folders=(self.spritespath,), names=("title", "credit farkas", "credit disa"))

        linkedsprites.clear()
        sprite_slicer(59, 44, outputlist=linkedsprites, folders=(self.spritespath,), name='asteroid_sprites1')
        self.asteroidsprites = Msr(self.window, images=linkedsprites)

        self.menustars = pygame.sprite.Group()

        for x in range(60):
            self.menustarsadd(True)

        pygame.mixer.music.load(os.path.join(self.audiopath, 'space.ogg'))

        self.asteroidsound = pygame.mixer.Sound(f'{self.audiopath}/crash.ogg')
        self.clearedsound = pygame.mixer.Sound(f'{self.audiopath}/cleared.ogg')
        self.boxsounds = tuple(pygame.mixer.Sound(f'{self.audiopath}/box{x + 1}.ogg') for x in range(4))
        self.boxhitsounds = tuple(pygame.mixer.Sound(f'{self.audiopath}/boxhit{x + 1}.ogg') for x in range(4))
        self.lasersounds = tuple(pygame.mixer.Sound(f'{self.audiopath}/laserShoot_{x+1}_.ogg') for x in range(4))
        entity.Laser.sounds = self.lasersounds
        self.laserhitsounds = tuple(pygame.mixer.Sound(f'{self.audiopath}/hitHurt_{x + 1}_.ogg') for x in range(4))
        entity.Laser.hitsounds = self.laserhitsounds

        self.audio()
        pygame.mixer.music.play(-1)

    def audio(self):
        #print('audio set')
        pygame.mixer.music.set_volume(self.soundvolume * 0.2)

        self.asteroidsound.set_volume(self.soundvolume)
        self.clearedsound.set_volume(self.soundvolume * 0.4)

        for sound in self.boxsounds:
            sound.set_volume(self.soundvolume * 0.17)
        for sound in self.boxhitsounds:
            sound.set_volume(self.soundvolume * 0.2)

        for sound in self.lasersounds:
            sound.set_volume(self.soundvolume * 0.1)
        for sound in self.laserhitsounds:
            sound.set_volume(self.soundvolume * 0.1)

    def events(self) -> float:
        # check for events
        fps_start = time.perf_counter()

        for event in pygame.event.get():
            if event.type == pygame.WINDOWRESIZED and not self.fullscreen:
                self.winresolution = self.window.size

            if event.type == pygame.QUIT:
                self.quit()

        fps_end = time.perf_counter()

        self.keyboard = (self.keyboard[1], pygame.key.get_pressed())
        self.mouse = [self.mouse[1], pygame.mouse.get_pressed()]

        rect = self.logical_sizeRect.fit(pygame.Rect(0, 0, *self.window.size))

        self.mousepos[0].update(self.mousepos[1])
        self.mousepos[1].update(pygame.mouse.get_pos())
        self.mousepos[1].x -= rect.x
        self.mousepos[1].y -= rect.y
        if not (self.mouse[1][0] or self.mouse[1][2] or self.mouse[1][1]):
            self.mousepos[1].x = pygame.math.clamp(self.mousepos[1].x, 0, rect.w)
            self.mousepos[1].y = pygame.math.clamp(self.mousepos[1].y, 0, rect.h)
        self.mousepos[1].x *= self.logical_sizeRect.w / rect.w
        self.mousepos[1].y *= self.logical_sizeRect.h / rect.h
        self.mousepos[1].x = round(self.mousepos[1].x)
        self.mousepos[1].y = round(self.mousepos[1].y)

        Button.mouse = self.mouse
        Button.mousepos = self.mousepos
        Button.keyboard = self.keyboard

        self.mouseclicked = 0
        if self.mouse[1][0] and not self.mouse[0][0]:
            self.mouseclicked = 1
        if self.mouseclicked:
            self.mouseclickpos = self.mousepos[1]

        return fps_end - fps_start

    def keys(self, keys):
        # keyboard controls check
        pressed = 0
        held = 0
        released = 0
        for key in keys:
            if self.keyboard[1][key]:
                held += 1
                if not self.keyboard[0][key]:
                    pressed += 1
            elif self.keyboard[0][key]:
                released += 1

        return pressed, held, released

    def movement(self):
        # movement input normal vector
        vect = pygame.Vector2(0, 0)
        keys = self.keyboard[1]
        if keys[self.controls['Left']] or keys[pygame.K_LEFT]:
            vect.x += 1
        if keys[self.controls['Right']] or keys[pygame.K_RIGHT]:
            vect.x -= 1
        if keys[self.controls['Up']] or keys[pygame.K_UP]:
            vect.y += 1
        if keys[self.controls['Down']] or keys[pygame.K_DOWN]:
            vect.y -= 1
        if vect.x != 0 or vect.y != 0:
            vect = vect.normalize()
            vect *= -1

        self.move = vect

    def resize(self, scale=None):
        if hasattr(platform, 'window'):
            return

        pygame.mouse.set_pos(0, 0)

        if scale is None:
            self.fullscreen = not self.fullscreen

            if self.fullscreen:
                self.window.set_fullscreen(True)
            else:
                self.window.set_windowed()
                self.winresolution = self.window.size
        else:
            rect = pygame.Rect(*self.window.position, *self.window.size)

            self.window.set_windowed()
            self.fullscreen = False
            self.winresolution = scale
            self.window.size = scale

            self.window.position = rect.centerx - self.window.size[0] / 2, rect.centery - self.window.size[1] / 2

        rect = self.logical_sizeRect.fit(pygame.Rect(0, 0, *self.window.size))
        pygame.mouse.set_pos(self.mousepos[1].x / 640 * rect.w + rect.x, self.mousepos[1].y / 360 * rect.h + rect.y)

    def quit(self):
        # print("Quiting game")

        self.running = False

        self.display.draw_color = "Black"
        self.display.clear()
        self.display.present()

        if not hasattr(platform, 'window'):
            self.display.target = None

    async def run(self):
        # start up
        self.mousepos = (pygame.Vector2(0, 0), pygame.Vector2(0, 0))
        self.keyboard = (pygame.key.get_pressed(), pygame.key.get_pressed())
        self.mouse = (pygame.mouse.get_pressed(), pygame.mouse.get_pressed())
        self.mouseclickpos = self.mousepos[1]
        self.mouseclicked = 0
        self.events()
        frame = 0

        if self.fullscreen:
            self.resize(self.winresolution)
            self.resize()
        else:
            self.resize(self.winresolution)

        while self.running:  # main loop
            fps_start = time.perf_counter()

            prevstate = Sm.state

            eventtime = self.events()

            # debug
            if self.keys((pygame.K_f,))[0]:
                self.resize((1024, 600) if self.fullscreen else None)

            self.display.draw_color = (0, 40, 0, 0)
            self.display.target = self.screen
            Msr.screenrect = self.logical_sizeRect
            self.display.clear()

            Sm.states[Sm.state]()

            self.display.target = None
            Msr.screenrect = self.display.get_viewport()
            self.display.draw_color = (0, 0, 0, 0)
            self.display.clear()

            self.screen.draw(dstrect=self.logical_sizeRect.fit(pygame.Rect(0, 0, *self.window.size)))

            self.display.present()

            Sm.prevstate = prevstate

            fps_end = time.perf_counter()
            dt = fps_end - fps_start - eventtime

            # debug fps
            if frame % 8 == 0 and dt:
                frame = 0
                self.window.title = f"FPS: {int(1 / dt)}, {round(self.clock.get_fps(), 1)} W:{self.window.size[0]} {self.window.size[1]}"
            frame += 1

            await asyncio.sleep(0)
            self.clock.tick(60)
            fps_end2 = time.perf_counter()
            self.dt = min(fps_end2 - fps_start - eventtime, 0.1)
            # print(self.clock.get_fps())


if __name__ == '__main__':
    app = App()
    asyncio.run(app.run())
