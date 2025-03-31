import asyncio
import platform
import pygame
import sys
import time
from pygame._sdl2.video import Window, Renderer, Texture
if sys.platform == "emscripten":
    platform.window.canvas.style.imageRendering = "pixelated"

from engine import StateMachine as Sm
from buttons import Button
from multi_sprite_renderer_hardware import MultiSprite as Msr
from assets import Assets
from particles import Particle

import menu
import scene


class App:

    def __init__(self):
        self.winresolution = 1024, 600
        self.fullscreen = False

        self.soundvolume = 0.5

        self.damagemult = 1
        self.scale = 1

        self.controls = {'Up': pygame.K_w,
                         'Down': pygame.K_s,
                         'Left': pygame.K_a,
                         'Right': pygame.K_d,
                         'Ok': pygame.K_SPACE,
                         'Esc': pygame.K_ESCAPE,
                         'Fullscreen': pygame.K_f
                         }

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

        self.dt = 0.016
        self.running = True

        Button.controls = self.controls

        Assets.makemsrs()
        Assets.makeaudio()

        menu.Menu()
        scene.Scene()

        Sm.app = self
        Sm.state = 'menu'
        Sm.loadin()

    def events(self) -> float:
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

        Button.input(self.mousepos, self.mouse, self.keyboard)

        self.mouseclicked = 0
        if self.mouse[1][0] and not self.mouse[0][0]:
            self.mouseclicked = 1
        if self.mouseclicked:
            self.mouseclickpos = self.mousepos[1]

        return fps_end - fps_start

    def keys(self, keys):
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
        pygame.mouse.set_pos(self.mousepos[1].x / self.logical_sizeRect.w * rect.w + rect.x, self.mousepos[1].y / self.logical_sizeRect.h * rect.h + rect.y)

    def quit(self):

        self.running = False
        pygame.mixer.music.stop()

        self.display.draw_color = "Black"
        self.display.clear()
        self.display.present()

        if not hasattr(platform, 'window'):
            self.display.target = None

    async def run(self):
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
            if self.keys((self.controls["Fullscreen"],))[0]:
                self.resize()

            self.display.draw_color = (0, 0, 0, 0)
            self.display.target = self.screen
            Msr.screenrect = self.logical_sizeRect
            self.display.clear()

            Particle.dt = self.dt

            Sm.states[Sm.state]()

            self.display.target = None
            Msr.screenrect = self.display.get_viewport()
            self.display.draw_color = (15, 15, 15, 0)
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


if __name__ == '__main__':
    app = App()
    asyncio.run(app.run())
