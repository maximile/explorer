import os
import copy
import pyglet

import man
import color
import pixmap

TOP = "TOP"
LEFT = "LEFT"
BOTTOM = "BOTTOM"
RIGHT = "RIGHT"


def file_for_coords(x, y):
    levels_dir = "levels"
    names = os.listdir(levels_dir)
    for name in names:
        try:
            test_x, test_y = [int(c) for c in name.split(".")[0].split(",")]
        except ValueError:
            continue
        if test_x == x and test_y == y:
            return os.path.join(levels_dir, name)


class Level(object):
    def __init__(self, x, y, rescued_mans=()):
        file_path = file_for_coords(x, y)
        if not file_path:
            raise ValueError("%i, %i" % x, y)
        self.coords = x, y
        
        # Can connect to others?
        self.connections = []
        if file_for_coords(x - 1, y):
            self.connections.append(LEFT)
        if file_for_coords(x + 1, y):
            self.connections.append(RIGHT)
        if file_for_coords(x, y + 1):
            self.connections.append(TOP)
        if file_for_coords(x, y - 1):
            self.connections.append(BOTTOM)
        
        image = pyglet.image.load(file_path)
        self.pixmap = pixmap.Pixmap.from_pyglet_image(image)
        
        # Sort out mans
        self.mans = man.get_mans_from_pixmap(self.pixmap)
        
        # Get rid of rescued ones
        for key in rescued_mans:
            if key in self.mans:
                del self.mans[key]
        
        # Get rid of tech pixels
        self._collision_map = copy.deepcopy(self.pixmap)
        self._collision_map.remove_colors(keep=(color.BLACK, color.WHITE))
        self.bg_sprite = pyglet.sprite.Sprite(self.collision_map.to_image())
        
        self.width = image.width
        self.height = image.height
        
    @property
    def collision_map(self):
        return self._collision_map

    def draw(self):
        self.bg_sprite.draw()
        for this_man in self.mans.values():
            this_man.draw()
