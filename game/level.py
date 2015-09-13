import ctypes
import pyglet


class Level(object):
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = pyglet.image.load(image_path)
        
        def is_red(r, g, b):
            return r > 200 and g < 50 and b < 50

        def is_black(r, g, b):
            return r < 50 and g < 50 and b < 50

        def is_white(r, g, b):
            return r > 250 and g > 250 and b > 250
        
        # Process image to find landing surfaces and start points
        self.checkpoints = []
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
        
        print self.checkpoints
        if not self.checkpoints:
            raise RuntimeError("No checkpoints.")
        
        self.bg_sprite = pyglet.sprite.Sprite(self.image)
        
        self.width = self.image.width
        self.height = self.image.height
        
        # Cache collision data
        data = self.image.get_image_data().get_data("R", self.image.width)
        if bg_col == (0, 0, 0):
            self._collision_mask = tuple([ord(d) >= 127 for d in data])
        else:
            self._collision_mask = tuple([ord(d) < 127 for d in data])
    
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
        pass