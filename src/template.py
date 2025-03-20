import pygame
from engine import StateMachine as Sm
from engine import Camera
from buttons import Button

from assets import Assets

class Template:

    def __init__(self):
        Sm.loadins.append(self.load)
        Sm.states.update({'template': self.template,
                          })

    def load(self):
        self.sprite = Assets.buttonsprites

        self.playB = Button(self.sprite, pos=(640 // 2, 180), popup=(1.1, 1.1), scale=(1, 0.2))
        self.buttons = [self.playB]

    def template(self):
        if Sm.prevstate != "template":
            for button in self.buttons:
                button.update("check")
            Button.selectedB = self.playB

        Assets.font_white.write(Sm.app.title, scale=(2, 2), pos=(320, 120), relativeOffset=(0, 0), align=1)

        Button.select(self.buttons)
        for button in self.buttons:
            button.update()

        if self.playB.clicked:
            # Game()
            pass

        if self.playB.clicked:
            Sm.state = "settings"

        if self.playB.clicked or Sm.app.keys((Sm.app.controls["Esc"],))[0]:
            Sm.app.quit()


template = Template()
