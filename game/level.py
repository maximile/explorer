import os
import pyglet

import man
# import geometry

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
        
        self.image = pyglet.image.load(file_path)
        
        def is_red(r, g, b):
            return r > 210 and g < 100 and b < 100

        def is_black(r, g, b):
            return r < 50 and g < 50 and b < 50

        def is_white(r, g, b):
            return r > 210 and g > 210 and b > 210
            
        def is_green(r, g, b):
            return r < 100 and g > 180 and b < 100
        
        print "HERE"
        man.get_mans_from_image(self.image)
        print "THERE"
        
        # Process image to find landing surfaces and start points
        self.checkpoints = []
        man_locs = []
        bg_col = None
        rgb_data = self.image.get_image_data().get_data("RGB", self.image.width * 3)
        for y in xrange(self.image.height):
            for x in xrange(self.image.width):
                r = ord(rgb_data[y * self.image.width * 3 + x * 3])
                g = ord(rgb_data[y * self.image.width * 3 + x * 3 + 1])
                b = ord(rgb_data[y * self.image.width * 3 + x * 3 + 2])
                if is_red(r, g, b):
                    self.checkpoints.append((x, y))
                    if bg_col is None:
                        g = ord(rgb_data[y * self.image.width * 3 + (x - 1) * 3 + 1])
                        if g < 127:
                            bg_col = 0, 0, 0
                        else:
                            bg_col = 255, 255, 255
                if is_green(r, g, b):
                    man_locs.append((x, y))
        self.bg_col = bg_col
        
        if not self.checkpoints:
            raise RuntimeError("No checkpoints.")
        
        # Sort out mans
        mans = man.get_mans_from_image(self.image)
        self.mans = {}
        for i, the_man in enumerate(mans):
            self.mans[i] = man
        
        # self.mans = {}
        # man_points = [geometry.Point(*loc) for loc in man_locs]
        # man_rects = geometry.get_rects_containing_points(man_points, threshold=8)
        
        # man_locs = []
        # for man_rect in man_rects:
        #     center = man_rect.center
        #     loc = int(center.x), int(center.y)
        #     man_locs.append(loc)
        # print man_locs
        
        # # print man_rects
        
        # for man_loc in man_locs:
        #     this_man = man.Man()
        #     this_man.pos = man_loc
        #     if self.bg_col == (255, 255, 255):
        #         this_man.color = man.BLACK
        #     else:
        #         this_man.color = man.WHITE
        #     self.mans[man_loc] = this_man
        
        # Get rid of rescued ones
        for key in rescued_mans:
            if key in self.mans:
                del self.mans[key]
        
        # Get rid of tech pixels
        new_data = ""
        for y in xrange(self.image.height):
            for x in xrange(self.image.width):
                r = ord(rgb_data[y * self.image.width * 3 + x * 3])
                g = ord(rgb_data[y * self.image.width * 3 + x * 3 + 1])
                b = ord(rgb_data[y * self.image.width * 3 + x * 3 + 2])
                
                if is_white(r, g, b):
                    new_data += chr(255) * 3 + chr(255)
                elif is_black(r, g, b):
                    new_data += chr(0) * 3 + chr(255)
                else:
                    new_data += "".join([chr(c) for c in bg_col]) + chr(255)

        self.image.set_data('RGBA', self.image.width * 4, new_data)
        self.bg_sprite = pyglet.sprite.Sprite(self.image)
        
        self.width = self.image.width
        self.height = self.image.height
        
        # Cache collision data
        data = self.image.get_image_data().get_data("R", self.image.width)
        if bg_col == (0, 0, 0):
            self._collision_mask = tuple([ord(d) >= 127 for d in data])
        else:
            self._collision_mask = tuple([ord(d) < 127 for d in data])
        
        # Floor mans
        for key, the_man in self.mans.items():
            while True:
                # Sample below
                x = the_man.pos[0] + the_man.width // 2
                y = the_man.pos[1] - 1
                if self._collision_mask[self.width * y + x]:
                    break
                the_man.pos = the_man.pos[0], the_man.pos[1] - 1
                if the_man.pos < 0:
                    raise RuntimeError("Too low!")

    def nearest_checkpoint(self, x, y):
        smallest_dist = 1000000.0
        closest = None
        for test_cp in self.checkpoints:
            dist = ((x - test_cp[0]) ** 2 + (y - test_cp[1]) ** 2) ** 0.5
            if dist < smallest_dist:
                smallest_dist = dist
                closest = test_cp
        return closest
    
    @property
    def collision_mask(self):
        return self._collision_mask

    def draw(self):
        self.bg_sprite.draw()
        for this_man in self.mans.values():
            this_man.draw()

