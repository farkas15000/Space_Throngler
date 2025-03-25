import random
import pygame
from engine import StateMachine as Sm
from buttons import Button, Slider

from assets import Assets
from particles import Particle


class Menu:

    def __init__(self):
        Sm.loadins.append(self.load)
        Sm.states.update({'menu': self.menu,
                          'menu_instance': self
                          })

    def load(self):
        self.startimer = 0
        self.menustartimer = 0
        self.trailtimer = 0
        self.asteroidrot = 23
        self.easteregg = 0

        self.startbutton = Button(sprites=Assets.startsprites, name=0, scale=(2, 2), pos=(512, 270),  relativeOffset=(0, 0), popup=(1.04, 1.04))
        self.soundslider = Slider(sprites=Assets.soundsprites, name=1, scale=(3, 3), pos=pygame.Vector2(0, 370), relativeOffset=(0, 0), popup=(1.04, 1.04), posmap=(531, 681), valuemap=(0, 100), stepsize=5)
        self.soundslider.value = Sm.app.soundvolume * 100
        self.mobilebutton = Button(sprites=Assets.mobilesprites, name=Sm.app.mobile, scale=(2, 2), pos=(1014, 12), relativeOffset=(0.5, -0.5), popup=(1, 1))
        self.exitbutton = Button(sprites=Assets.buttonsprites, name=0, scale=(2, 2), relativeOffset=(-0.5, -0.5),
                                 popup=(1.06, 1.06))
        self.exitbutton.scale = (3, 3)

        self.mobiletoggle = not Sm.app.mobile

        self.eastereggknob = Slider(sprites=Assets.soundsprites, name=1, scale=(3, 3), pos=pygame.Vector2(0, 370), relativeOffset=(0, 0), popup=(1.04, 1.04), posmap=(84, 234), valuemap=(50, 400), stepsize=1)
        self.eastereggknob.value = Sm.app.scale * 100

        self.starparticles = pygame.sprite.Group()
        self.menustars = pygame.sprite.Group()
        for x in range(60):
            self.menustarsadd(True)

        self.audio()
        pygame.mixer.music.play(-1)

    def menu(self):
        if Sm.prevstate != "menu":
            self.startimer = 0
            self.menustartimer = 0
            self.trailtimer = 0
            self.asteroidrot = 23

            self.exitbutton.scale = (3, 3)

        self.dt = Sm.app.dt

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
                trail = Particle(pos=(880 + random.randint(-20, 20), 305 + random.randint(-40, 40)),
                                 sprites=Assets.particlesprites,
                                 animation=(random.uniform(0.3, 0.45), 4),
                                 velocity=pygame.Vector2(random.randint(280, 320), 0).rotate(-rot),
                                 scale=(4, 4), rotation=rot + 180)
                self.menustars.add(trail)

        self.asteroidrot -= 45 * self.dt
        asteroid = Assets.asteroidsprites.draw(0, scale=(3, 3), pos=(880, 305), relativeOffset=(0, 0), rotation=self.asteroidrot)[0]
        if Sm.app.mouseclicked and self.easteregg < 10 and asteroid.collidepoint(Button.mousepos[1]):
            self.easteregg += 1
            Assets.clearedsound.play()

        if self.easteregg >= 10:
            Assets.eastereggsprite.draw(0, scale=(2, 2), pos=(120, 235))
            Assets.soundsprites.draw(2, scale=(1, 1), pos=(60, 370), relativeOffset=(-0.5, 0))

            scale = self.eastereggknob.value
            self.eastereggknob.update()
            if scale != self.eastereggknob.value:
                Sm.app.scale = round(self.eastereggknob.value / 100, 1)
            Assets.font_white.write(f'Size:{round(Sm.app.scale, 1)}x', scale=(2, 2), pos=(52, 400))

        Assets.menu_texts_msr.draw(0, scale=(3, 3), pos=(512, 150), relativeOffset=(0, 0))
        Assets.menu_texts_msr.draw(1, scale=(2, 2), pos=(512, 480), relativeOffset=(0, 0))

        eyepos = pygame.Vector2(599, 151)
        relativeOffset = -eyepos + Button.mousepos[1]
        if relativeOffset:
            relativeOffset = relativeOffset.normalize() * 3
        relativeOffset.x *= 1.4
        Assets.monstersprites.draw(name=1, scale=(1.6, 1.6), pos=eyepos + relativeOffset, relativeOffset=(0, 0))

        self.exitbutton.update()
        self.startbutton.update()

        Assets.soundsprites.draw(0, scale=(2, 2), pos=(475, 370), relativeOffset=(0.5, 0))
        Assets.soundsprites.draw(2, scale=(1, 1), pos=(507, 370), relativeOffset=(-0.5, 0))

        volume = self.soundslider.value
        self.soundslider.update()
        if Sm.app.keys((Sm.app.controls['Left'], pygame.K_LEFT, Sm.app.controls['Down'], pygame.K_DOWN))[0]:
            self.soundslider.value -= self.soundslider.stepsize
        if Sm.app.keys((Sm.app.controls['Right'], pygame.K_RIGHT, Sm.app.controls['Up'], pygame.K_UP))[0]:
            self.soundslider.value += self.soundslider.stepsize
        if volume != self.soundslider.value:
            Sm.app.soundvolume = self.soundslider.value / 100
            self.audio()

        self.mobilebutton.update()
        if self.mobilebutton.clicked and self.mobiletoggle:
            Sm.app.mobile = not Sm.app.mobile
            self.mobilebutton.name = Sm.app.mobile

        if Sm.app.keys((Sm.app.controls['Esc'],))[0] or self.exitbutton.clicked:
            Sm.app.quit()

        if Sm.app.keys((Sm.app.controls['Ok'], pygame.K_RETURN))[0] or self.startbutton.clicked:
            Sm.state = "scene"

    @staticmethod
    def audio():
        pygame.mixer.music.set_volume(Sm.app.soundvolume * 0.2)

        Assets.asteroidsound.set_volume(Sm.app.soundvolume)
        Assets.clearedsound.set_volume(Sm.app.soundvolume * 0.4)

        for sound in Assets.boxsounds:
            sound.set_volume(Sm.app.soundvolume * 0.17)
        for sound in Assets.boxhitsounds:
            sound.set_volume(Sm.app.soundvolume * 0.2)

        for sound in Assets.lasersounds:
            sound.set_volume(Sm.app.soundvolume * 0.1)
        for sound in Assets.laserhitsounds:
            sound.set_volume(Sm.app.soundvolume * 0.1)

    def stars(self):
        self.starparticles.update('loop')
        if self.startimer <= 0:
            self.startimer = random.uniform(0.8, 1)
            speedrange = (40, 60)

            for star in ((1040, 15, 25, 1040, 42, 180), (1040, 575, 585, 1040, 420, 558), (446, 15, 25, 40, 42, 190), (446, 575, 585, 40, 410, 558)):
                speed = random.randint(*speedrange)
                particle = Particle(pos=(star[0], random.randint(star[1], star[2])), sprites=Assets.particlesprites,
                                    animation=(460 / speed, 1 + random.randrange(3)),
                                    velocity=(-speed, 0),
                                    scale=(2, 2), rotation=random.randrange(10) * 36 + 6,
                                    relativeOffset=(random.uniform(-1, 1), random.uniform(-1, 1)))
                self.starparticles.add(particle)

                for z in range(2):
                    speed = random.randint(*speedrange)
                    particle = Particle(pos=(star[3], random.randint(star[4], star[5])), sprites=Assets.particlesprites,
                                        animation=(55/speed, 1+random.randrange(3)),
                                        velocity=(-speed, 0),
                                        scale=(2, 2), rotation=random.randrange(10) * 36+15,
                                        relativeOffset=(random.uniform(-1, 1), random.uniform(-1, 1)))
                    self.starparticles.add(particle)

    def menustarsadd(self, preload=False):

        speed = random.randint(40, 60)
        particle = Particle(pos=(random.randint(15, 1009) if preload else 1040, random.randint(5, 595)), sprites=Assets.particlesprites,
                            animation=(1080 / speed, 1 + random.randrange(3)),
                            velocity=(-speed, 0),
                            scale=(2, 2), rotation=random.randrange(10) * 36 + 15,
                            relativeOffset=(random.uniform(-1, 1), random.uniform(-1, 1)))
        self.menustars.add(particle)
