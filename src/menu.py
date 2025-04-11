import random
import pygame
from engine import StateMachine as Sm
from buttons import Button, Slider

from assets import Assets
from particles import Particle


class Menu:

    def __init__(self):
        Sm.loadIns.append(self.load)
        Sm.states.update({"menu": self.menu, "menu_instance": self})

        self.starTimer = 0
        self.menuStarTimer = 0
        self.trailTimer = 0
        self.asteroidRot = 23
        self.easterEgg = 0
        self.dt = 0

        self.startButton = None
        self.easterEggSlider = None
        self.mobileToggle = None
        self.exitButton = None
        self.mobileButton = None
        self.soundSlider = None

        self.starParticles = pygame.sprite.Group()
        self.menuStars = pygame.sprite.Group()

    def load(self):
        self.startButton = Button(
            sprites=Assets.startSprites,
            name=0,
            scale=(2, 2),
            pos=(512, 270),
            relativeOffset=(0, 0),
            popup=(1.04, 1.04),
        )
        self.soundSlider = Slider(
            sprites=Assets.soundSprites,
            name=1,
            scale=(3, 3),
            pos=pygame.Vector2(0, 370),
            relativeOffset=(0, 0),
            popup=(1.04, 1.04),
            pos_map=(531, 681),
            value_map=(0, 100),
            step_size=5,
        )
        self.soundSlider.value = Sm.app.soundVolume * 100
        self.mobileButton = Button(
            sprites=Assets.mobileSprites,
            name=Sm.app.mobile,
            scale=(2, 2),
            pos=(1014, 12),
            relativeOffset=(0.5, -0.5),
            popup=(1, 1),
        )
        self.exitButton = Button(
            sprites=Assets.buttonSprites,
            name=0,
            scale=(2, 2),
            relativeOffset=(-0.5, -0.5),
            popup=(1.06, 1.06),
        )
        self.exitButton.scale = (3, 3)

        self.mobileToggle = not Sm.app.mobile

        self.easterEggSlider = Slider(
            sprites=Assets.soundSprites,
            name=1,
            scale=(3, 3),
            pos=pygame.Vector2(0, 370),
            relativeOffset=(0, 0),
            popup=(1.04, 1.04),
            pos_map=(84, 234),
            value_map=(50, 400),
            step_size=1,
        )
        self.easterEggSlider.value = Sm.app.monsterScale * 100

        for x in range(60):
            self.menuStarsAdd(True)

        self.audio()
        pygame.mixer.music.play(-1)

    def menu(self):
        # back to menu
        if Sm.prevState != "menu":
            self.starTimer = 0
            self.menuStarTimer = 0
            self.trailTimer = 0
            self.asteroidRot = 23

            self.exitButton.scale = (3, 3)

        self.dt = Sm.app.dt

        self.starTimer -= self.dt
        self.stars()

        self.menuStarTimer -= self.dt
        if self.menuStarTimer <= 0:
            self.menuStarTimer = random.uniform(0.2, 0.5)
            self.menuStarsAdd()
        self.menuStars.update()

        self.trailTimer -= self.dt
        if self.trailTimer <= 0:
            self.trailTimer = random.uniform(0.05, 0.1)
            for z in range(5):
                rot = random.randint(160, 200)
                trail = Particle(
                    pos=(
                        880 + random.randint(-20, 20),
                        305 + random.randint(-40, 40),
                    ),
                    sprites=Assets.particleSprites,
                    animation=(random.uniform(0.3, 0.45), 4),
                    velocity=pygame.Vector2(
                        random.randint(280, 320), 0
                    ).rotate(-rot),
                    scale=(4, 4),
                    rotation=rot + 180,
                )
                self.menuStars.add(trail)

        self.asteroidRot -= 45 * self.dt
        asteroid = Assets.asteroidSprites.draw(
            0,
            scale=(3, 3),
            pos=(880, 305),
            relativeOffset=(0, 0),
            rotation=self.asteroidRot,
        )[0]
        if (
            Sm.app.mouseClicked
            and self.easterEgg < 10
            and asteroid.collidepoint(Button.mousePos[1])
        ):
            self.easterEgg += 1
            Assets.clearedSound.play()

        if self.easterEgg >= 10:
            Assets.easterEggSprite.draw(0, scale=(2, 2), pos=(120, 235))
            Assets.soundSprites.draw(
                2, scale=(1, 1), pos=(60, 370), relativeOffset=(-0.5, 0)
            )

            scale = self.easterEggSlider.value
            self.easterEggSlider.update()
            if scale != self.easterEggSlider.value:
                Sm.app.monsterScale = round(
                    self.easterEggSlider.value / 100, 1
                )
            Assets.font_white.write(
                f"Size:{round(Sm.app.monsterScale, 1)}x",
                scale=(2, 2),
                pos=(52, 400),
            )

        Assets.menuTextSprites.draw(
            0, scale=(3, 3), pos=(512, 150), relativeOffset=(0, 0)
        )
        Assets.font_white.write(
            "Készítette: Füleki Balázs",
            pos=Sm.app.logical_sizeRect.midbottom,
            relativeOffset=(0, 1),
            scale=(2, 2),
        )

        # eye draw in title
        eye_pos = pygame.Vector2(599, 151)
        offset = -eye_pos + Button.mousePos[1]
        if offset:
            offset = offset.normalize() * -3
        offset.x *= 1.4
        Assets.monsterSprites.draw(
            name=1,
            scale=(1.6, 1.6),
            pos=eye_pos,
            relativeOffset=(0, 0),
            offset=offset,
        )

        self.exitButton.update()
        self.startButton.update()

        Assets.soundSprites.draw(
            0, scale=(2, 2), pos=(475, 370), relativeOffset=(0.5, 0)
        )
        Assets.soundSprites.draw(
            2, scale=(1, 1), pos=(507, 370), relativeOffset=(-0.5, 0)
        )

        # volume slider
        volume = self.soundSlider.value
        self.soundSlider.update()
        if Sm.app.keys(
            (
                Sm.app.controls["Left"],
                pygame.K_LEFT,
                Sm.app.controls["Down"],
                pygame.K_DOWN,
            )
        )[0]:
            self.soundSlider.value -= self.soundSlider.stepSize
        if Sm.app.keys(
            (
                Sm.app.controls["Right"],
                pygame.K_RIGHT,
                Sm.app.controls["Up"],
                pygame.K_UP,
            )
        )[0]:
            self.soundSlider.value += self.soundSlider.stepSize
        if volume != self.soundSlider.value:
            Sm.app.soundVolume = self.soundSlider.value / 100
            self.audio()

        self.mobileButton.update()
        if self.mobileButton.clicked and self.mobileToggle:
            Sm.app.mobile = not Sm.app.mobile
            self.mobileButton.name = Sm.app.mobile

        if (
            Sm.app.keys((Sm.app.controls["Esc"],))[0]
            or self.exitButton.clicked
        ):
            Sm.app.quit()

        if (
            Sm.app.keys((Sm.app.controls["Ok"], pygame.K_RETURN))[0]
            or self.startButton.clicked
        ):
            Sm.state = "scene"

    @staticmethod
    def audio():
        """sets audio volume levels"""
        pygame.mixer.music.set_volume(Sm.app.soundVolume * 0.2)

        Assets.asteroidSound.set_volume(Sm.app.soundVolume)
        Assets.clearedSound.set_volume(Sm.app.soundVolume * 0.4)

        for sound in Assets.boxSounds:
            sound.set_volume(Sm.app.soundVolume * 0.17)
        for sound in Assets.boxHitSounds:
            sound.set_volume(Sm.app.soundVolume * 0.2)

        for sound in Assets.laserSounds:
            sound.set_volume(Sm.app.soundVolume * 0.1)
        for sound in Assets.laserHitSounds:
            sound.set_volume(Sm.app.soundVolume * 0.1)

    def stars(self):
        self.starParticles.update("loop")
        if self.starTimer <= 0:
            self.starTimer = random.uniform(0.8, 1)
            speed_range = (40, 60)

            for star in (
                (1040, 15, 25, 1040, 42, 180),
                (1040, 575, 585, 1040, 420, 558),
                (446, 15, 25, 40, 42, 190),
                (446, 575, 585, 40, 410, 558),
            ):
                speed = random.randint(*speed_range)
                particle = Particle(
                    pos=(star[0], random.randint(star[1], star[2])),
                    sprites=Assets.particleSprites,
                    animation=(460 / speed, 1 + random.randrange(3)),
                    velocity=(-speed, 0),
                    scale=(2, 2),
                    rotation=random.randrange(10) * 36 + 6,
                    relativeOffset=(
                        random.uniform(-1, 1),
                        random.uniform(-1, 1),
                    ),
                )
                self.starParticles.add(particle)

                for z in range(2):
                    speed = random.randint(*speed_range)
                    particle = Particle(
                        pos=(star[3], random.randint(star[4], star[5])),
                        sprites=Assets.particleSprites,
                        animation=(55 / speed, 1 + random.randrange(3)),
                        velocity=(-speed, 0),
                        scale=(2, 2),
                        rotation=random.randrange(10) * 36 + 15,
                        relativeOffset=(
                            random.uniform(-1, 1),
                            random.uniform(-1, 1),
                        ),
                    )
                    self.starParticles.add(particle)

    def menuStarsAdd(self, preload=False):

        speed = random.randint(40, 60)
        particle = Particle(
            pos=(
                random.randint(15, 1009) if preload else 1040,
                random.randint(5, 595),
            ),
            sprites=Assets.particleSprites,
            animation=(1080 / speed, 1 + random.randrange(3)),
            velocity=(-speed, 0),
            scale=(2, 2),
            rotation=random.randrange(10) * 36 + 15,
            relativeOffset=(random.uniform(-1, 1), random.uniform(-1, 1)),
        )
        self.menuStars.add(particle)
