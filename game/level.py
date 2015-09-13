import ctypes
import pyglet


class Level(object):
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = pyglet.image.load(image_path)
        self.bg_sprite = pyglet.sprite.Sprite(self.image)
        
        self.width = self.image.width
        self.height = self.image.height
        
        # Cache collision data
        data = self.image.get_image_data().get_data("R", self.image.width)
        self._collision_mask = tuple([ord(d) < 127 for d in data])

    @property
    def collision_mask(self):
        return self._collision_mask

    def draw(self):
        self.bg_sprite.draw()
        pass