import os.path
import pygame
from multi_sprite_renderer_hardware import MultiSprite as Msr

absPath = os.path.dirname(os.path.abspath(__name__))

spritesPath = os.path.join(absPath, "assets", "sprites")
audioPath = os.path.join(absPath, "assets", "audio")
fontPath = os.path.join(absPath, "assets", "fonts")


def sprite_slicer(
    width,
    height,
    wpad=0,
    hpad=0,
    output_list=None,
    folders=(),
    name="",
    surface=None,
):
    """
    cuts up image from file name or Surface
    with optional padding and output list
    """

    if width <= 0 or height <= 0:
        raise Exception("need area!")

    if surface is None:
        img = pygame.image.load(os.path.join(*folders, name + ".png"))
    else:
        img = surface
    imgh = img.get_height()
    col = 0
    if output_list is None:
        output_list = []

    while imgh // height > 0:
        imgw = img.get_width()
        row = 0
        while imgw // width > 0:
            imgw -= width + wpad
            surface = img.subsurface(
                pygame.Rect(
                    row * (width + wpad), col * (height + hpad), width, height
                )
            )
            output_list.append(surface)
            row += 1

        imgh -= height + hpad
        col += 1

    return output_list


class Assets:
    """Asset loader"""

    font_black = Msr()
    font_white = Msr()
    ship = Msr()
    shade = Msr()
    doorSprites = Msr()
    rocketSprites = Msr()
    monsterSprites = Msr()
    boxSprites = Msr()
    astronautSprites = Msr()
    laserSprites = Msr()
    bloodSprites = Msr()
    particleSprites = Msr()
    buttonSprites = Msr()
    pauseSprites = Msr()
    startSprites = Msr()
    soundSprites = Msr()
    easterEggSprite = Msr()
    mobileSprites = Msr()
    menuTextSprites = Msr()
    asteroidSprites = Msr()

    asteroidSound: pygame.mixer.Sound
    clearedSound: pygame.mixer.Sound
    boxSounds: tuple[pygame.mixer.Sound, ...]
    boxHitSounds: tuple[pygame.mixer.Sound, ...]
    laserSounds: tuple[pygame.mixer.Sound, ...]
    laserHitSounds: tuple[pygame.mixer.Sound, ...]

    @classmethod
    def makeMsrs(cls):
        """creates all textures for the game"""
        color_key = (163, 73, 164)

        linked_sprites = []

        cls.font_black(
            folders=(fontPath,),
            font="VCR_OSD_MONO_1.001",
            size=21,
            color="Black",
        )
        cls.font_white = Msr(
            folders=(fontPath,), font="VCR_OSD_MONO_1.001", size=21
        )

        ship = pygame.image.load(os.path.join(spritesPath, "ship5" + ".png"))
        ship.fill((234, 234, 234, 255), (50, 18, 412, 264))
        ship.set_colorkey(color_key)
        ship = pygame.transform.scale_by(ship, 2)
        cls.ship = Msr(images=(ship,))

        shade = pygame.Surface((1, 1))
        cls.shade = Msr(images=(shade,))

        doors = pygame.image.load(os.path.join(spritesPath, "doors1" + ".png"))
        doors.set_colorkey(color_key)
        doors = pygame.transform.scale_by(doors, 2)
        sprite_slicer(
            30 * 2,
            36 * 2,
            wpad=2 * 2,
            output_list=linked_sprites,
            surface=doors,
        )
        cls.doorSprites = Msr(images=linked_sprites)

        rocket = pygame.image.load(
            os.path.join(spritesPath, "rocket" + ".png")
        )
        rocket.set_colorkey(color_key)
        rocket = pygame.transform.scale_by(rocket, 2)
        cls.rocketSprites = Msr(images=(rocket,))

        healthbox = pygame.Surface((32, 8))
        healthbox.fill((255, 255, 255, 255), (1, 1, 30, 6))
        health = pygame.Surface((32, 8))
        health.fill(color_key)
        health.set_colorkey(color_key)
        health.fill((138, 15, 52), (1, 1, 30, 6))
        cls.monsterSprites = Msr(
            folders=(spritesPath,),
            names=("head", "eye", "limb", "joint"),
            images=(healthbox, health),
        )

        linked_sprites.clear()
        sprite_slicer(
            22,
            22,
            output_list=linked_sprites,
            folders=(spritesPath,),
            name="box_sprites1",
        )
        boxoutline = pygame.image.load(
            os.path.join(spritesPath, "boxoutline" + ".png")
        )
        boxoutline.set_colorkey(color_key)
        linked_sprites.append(boxoutline)
        boxshadow = pygame.Surface((22, 22))
        linked_sprites.append(boxshadow)
        cls.boxSprites = Msr(images=linked_sprites)

        linked_sprites.clear()
        sprite_slicer(
            24,
            24,
            output_list=linked_sprites,
            folders=(spritesPath,),
            name="astronaut_walk_sprites1",
        )
        sprite_slicer(
            24,
            24,
            output_list=linked_sprites,
            folders=(spritesPath,),
            name="astronaut_die_sprites1",
        )
        cls.astronautSprites = Msr(images=linked_sprites)

        cls.laserSprites = Msr(folders=(spritesPath,), names=("laser1",))

        linked_sprites.clear()
        sprite_slicer(
            6,
            6,
            wpad=1,
            hpad=1,
            output_list=linked_sprites,
            folders=(spritesPath,),
            name="blood1",
        )
        cls.bloodSprites = Msr(images=linked_sprites)

        particles = pygame.image.load(
            os.path.join(spritesPath, "particles1" + ".png")
        )
        particles.set_colorkey(color_key)
        linked_sprites.clear()
        sprite_slicer(
            7, 7, wpad=1, hpad=1, output_list=linked_sprites, surface=particles
        )
        cls.particleSprites = Msr(images=linked_sprites)

        exit_b = pygame.image.load(os.path.join(spritesPath, "exit" + ".png"))
        exit_b.set_colorkey(color_key)
        cls.buttonSprites = Msr(images=(exit_b,))

        linked_sprites.clear()
        pause = pygame.image.load(os.path.join(spritesPath, "pause" + ".png"))
        pause.set_colorkey(color_key)
        sprite_slicer(38, 20, output_list=linked_sprites, surface=pause)
        cls.pauseSprites = Msr(images=linked_sprites)

        cls.startSprites = Msr(folders=(spritesPath,), names=("start1",))

        soundbar = pygame.Surface((198, 16))
        soundbar.fill((255, 255, 255, 255))
        cls.soundSprites = Msr(
            folders=(spritesPath,),
            names=("sound", "sound knob"),
            images=(soundbar,),
        )

        cls.easterEggSprite = Msr(
            folders=(spritesPath,), names=("easter egg",)
        )

        linked_sprites.clear()
        sprite_slicer(
            144,
            32,
            output_list=linked_sprites,
            folders=(spritesPath,),
            name="mobile_sprites1",
        )
        cls.mobileSprites = Msr(images=linked_sprites)

        cls.menuTextSprites = Msr(folders=(spritesPath,), names=("title",))

        linked_sprites.clear()
        sprite_slicer(
            59,
            44,
            output_list=linked_sprites,
            folders=(spritesPath,),
            name="asteroid_sprites1",
        )
        cls.asteroidSprites = Msr(images=linked_sprites)

    @classmethod
    def makeAudio(cls):
        """creates all audio for the game"""

        pygame.mixer.music.load(os.path.join(audioPath, "space.ogg"))

        cls.asteroidSound = pygame.mixer.Sound(f"{audioPath}/crash.ogg")
        cls.clearedSound = pygame.mixer.Sound(f"{audioPath}/cleared.ogg")
        cls.boxSounds = tuple(
            pygame.mixer.Sound(f"{audioPath}/box{x + 1}.ogg") for x in range(4)
        )
        cls.boxHitSounds = tuple(
            pygame.mixer.Sound(f"{audioPath}/boxhit{x + 1}.ogg")
            for x in range(4)
        )
        cls.laserSounds = tuple(
            pygame.mixer.Sound(f"{audioPath}/laserShoot_{x + 1}_.ogg")
            for x in range(4)
        )
        cls.laserHitSounds = tuple(
            pygame.mixer.Sound(f"{audioPath}/hitHurt_{x + 1}_.ogg")
            for x in range(4)
        )
