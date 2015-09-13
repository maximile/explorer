import pyglet
import random

BLACK = "BLACK"
WHITE = "WHITE"
LEFT = "LEFT"
RIGHT = "RIGHT"


class Man(object):
    def __init__(self):
        self.color = BLACK
        self.pos = 0, 0
        self.direction = random.choice([LEFT, RIGHT])

        paths_for_colors = {BLACK: "images/man_black.psd",
                            WHITE: "images/man_white.psd"}
        self.sprites = {}
        for color, path in paths_for_colors.items():
            image = pyglet.image.load(path)
            self.height = image.height
            self.width = image.width // 2
            seq = pyglet.image.ImageGrid(image, 1, 2)
            dur = random.uniform(0.2, 0.3)
            anim = pyglet.image.Animation.from_image_sequence(seq, dur, True)
            self.sprites[color] = pyglet.sprite.Sprite(anim)
    
    def draw(self):
        sprite = self.sprites[self.color]
        sprite.x, sprite.y = self.pos
        sprite.draw()
