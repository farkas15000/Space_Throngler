import os.path
import pygame
from multi_sprite_renderer_hardware import MultiSprite as Msr

abspath = os.path.dirname(os.path.abspath(__name__))
print(abspath)

spritespath = os.path.join(abspath, 'assets', 'sprites')
audiopath = os.path.join(abspath, 'assets', 'audio')
fontpath = os.path.join(abspath, 'assets', 'fonts')


def sprite_slicer(width, height, wpad=0, hpad=0, outputlist=None, folders=(), name='', sprite=None):
    # cuts up image from file or Surface with optional padding and output list

    if width <= 0 or height <= 0:
        raise Exception('need area!')

    if sprite is None:
        img = pygame.image.load(os.path.join(*folders, name + '.png'))
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


class Assets:

    font_black = Msr()
    font_white = Msr()
    ship = Msr()
    shade = Msr()
    doorsprites = Msr()
    rocketsprites = Msr()
    monstersprites = Msr()
    boxsprites = Msr()
    astronautsprites = Msr()
    lasersprites = Msr()
    bloodsprites = Msr()
    particlesprites = Msr()
    buttonsprites = Msr()
    pausesprites = Msr()
    startsprites = Msr()
    soundsprites = Msr()
    eastereggsprite = Msr()
    mobilesprites = Msr()
    menu_texts_msr = Msr()
    asteroidsprites = Msr()

    asteroidsound: pygame.mixer.Sound
    clearedsound: pygame.mixer.Sound
    boxsounds: tuple[pygame.mixer.Sound]
    boxhitsounds: tuple[pygame.mixer.Sound]
    lasersounds: tuple[pygame.mixer.Sound]
    laserhitsounds: tuple[pygame.mixer.Sound]

    @classmethod
    def makemsrs(cls):
        colorkey = (163, 73, 164)

        linkedsprites = []

        cls.font_black(folders=(fontpath,), font='VCR_OSD_MONO_1.001', size=21, color='Black')
        cls.font_white = Msr(folders=(fontpath,), font='VCR_OSD_MONO_1.001', size=21)

        ship = pygame.image.load(os.path.join(spritespath, 'ship5' + '.png'))
        ship.fill((234, 234, 234, 255), (50, 18, 412, 264))
        ship.set_colorkey(colorkey)
        ship = pygame.transform.scale_by(ship, 2)
        cls.ship = Msr(images=(ship,))

        # todo
        shade = pygame.Surface((1, 1))
        cls.shade = Msr(images=(shade,))

        doors = pygame.image.load(os.path.join(spritespath, 'doors1' + '.png'))
        doors.set_colorkey(colorkey)
        doors = pygame.transform.scale_by(doors, 2)
        sprite_slicer(30 * 2, 36 * 2, wpad=2 * 2, outputlist=linkedsprites, sprite=doors)
        cls.doorsprites = Msr(images=linkedsprites)

        rocket = pygame.image.load(os.path.join(spritespath, 'rocket' + '.png'))
        rocket.set_colorkey(colorkey)
        rocket = pygame.transform.scale_by(rocket, 2)
        cls.rocketsprites = Msr(images=(rocket,))

        healthbox = pygame.Surface((32, 8))
        healthbox.fill((255, 255, 255, 255), (1, 1, 30, 6))
        health = pygame.Surface((32, 8))
        health.fill(colorkey)
        health.set_colorkey(colorkey)
        health.fill((138, 15, 52), (1, 1, 30, 6))
        cls.monstersprites = Msr(folders=(spritespath,), names=("head", "eye", "limb", "joint"), images=(healthbox, health))

        linkedsprites.clear()
        sprite_slicer(22, 22, outputlist=linkedsprites, folders=(spritespath,), name='box_sprites1')
        boxoutline = pygame.image.load(os.path.join(spritespath, 'boxoutline' + '.png'))
        boxoutline.set_colorkey(colorkey)
        linkedsprites.append(boxoutline)
        sprite_slicer(22, 22, outputlist=linkedsprites, folders=(spritespath,), name='box_shadow_sprites')
        cls.boxsprites = Msr(images=linkedsprites)

        linkedsprites.clear()
        sprite_slicer(24, 24, outputlist=linkedsprites, folders=(spritespath,), name='astronaut_walk_sprites1')
        sprite_slicer(24, 24, outputlist=linkedsprites, folders=(spritespath,), name='astronaut_die_sprites1')
        cls.astronautsprites = Msr(images=linkedsprites)

        cls.lasersprites = Msr(folders=(spritespath,), names=("laser1",))

        linkedsprites.clear()
        sprite_slicer(6, 6, wpad=1, hpad=1, outputlist=linkedsprites, folders=(spritespath,), name='blood1')
        cls.bloodsprites = Msr(images=linkedsprites)

        particles = pygame.image.load(os.path.join(spritespath, 'particles1' + '.png'))
        particles.set_colorkey(colorkey)
        linkedsprites.clear()
        sprite_slicer(7, 7, wpad=1, hpad=1, outputlist=linkedsprites, sprite=particles)
        cls.particlesprites = Msr(images=linkedsprites)

        exitB = pygame.image.load(os.path.join(spritespath, 'exit' + '.png'))
        exitB.set_colorkey(colorkey)
        cls.buttonsprites = Msr(images=(exitB,))

        linkedsprites.clear()
        pauseB = pygame.image.load(os.path.join(spritespath, 'pause' + '.png'))
        pauseB.set_colorkey(colorkey)
        sprite_slicer(38, 20, outputlist=linkedsprites, sprite=pauseB)
        cls.pausesprites = Msr(images=linkedsprites)

        cls.startsprites = Msr(folders=(spritespath,), names=('start1',))

        soundbar = pygame.Surface((198, 16))
        soundbar.fill((255, 255, 255, 255))
        cls.soundsprites = Msr(folders=(spritespath,), names=('sound', 'sound knob'),
                                images=(soundbar,))

        cls.eastereggsprite = Msr(folders=(spritespath,), names=("easter egg",))

        linkedsprites.clear()
        sprite_slicer(144, 32, outputlist=linkedsprites, folders=(spritespath,), name='mobile_sprites1')
        cls.mobilesprites = Msr(images=linkedsprites)

        cls.menu_texts_msr = Msr(folders=(spritespath,), names=("title", "credit farkas", "credit disa"))

        linkedsprites.clear()
        sprite_slicer(59, 44, outputlist=linkedsprites, folders=(spritespath,), name='asteroid_sprites1')
        cls.asteroidsprites = Msr(images=linkedsprites)

    @classmethod
    def makeaudio(cls):

        pygame.mixer.music.load(os.path.join(audiopath, 'space.ogg'))

        cls.asteroidsound = pygame.mixer.Sound(f'{audiopath}/crash.ogg')
        cls.clearedsound = pygame.mixer.Sound(f'{audiopath}/cleared.ogg')
        cls.boxsounds = tuple(pygame.mixer.Sound(f'{audiopath}/box{x + 1}.ogg') for x in range(4))
        cls.boxhitsounds = tuple(pygame.mixer.Sound(f'{audiopath}/boxhit{x + 1}.ogg') for x in range(4))
        cls.lasersounds = tuple(pygame.mixer.Sound(f'{audiopath}/laserShoot_{x + 1}_.ogg') for x in range(4))
        cls.laserhitsounds = tuple(pygame.mixer.Sound(f'{audiopath}/hitHurt_{x + 1}_.ogg') for x in range(4))
