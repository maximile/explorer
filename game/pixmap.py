import array
import pyglet

import color


class Pixmap(object):
    @classmethod
    def from_pyglet_image(cls, image):
        def _get_colors_for_image():
            if hasattr(image, "format") and image.format == "RGB":
                data_str = image.get_data("RGB", image.width * 3)
                for i in xrange(image.width * image.height):
                    r = ord(data_str[i * 4])
                    g = ord(data_str[i * 4 + 1])
                    b = ord(data_str[i * 4 + 2])
                    yield color.get_color_for_rgba(r, g, b, 255)

            else:
                data_str = image.get_data("RGBA", image.width * 4)
                for i in xrange(image.width * image.height):
                    r = ord(data_str[i * 4])
                    g = ord(data_str[i * 4 + 1])
                    b = ord(data_str[i * 4 + 2])
                    a = ord(data_str[i * 4 + 3])
                    yield color.get_color_for_rgba(r, g, b, a)
        
        data = array.array("B", _get_colors_for_image())
        return Pixmap(image.width, image.height, data)
    
    def __init__(self, width, height, data=None):
        self.data = data
        self.width = width
        self.height = height
    
    def __getitem__(self, key):
        x, y = key
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise IndexError(key)
        index = y * self.width + x
        return self.data[index]
    
    def __setitem__(self, key, value):
        x, y = key
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise IndexError(key)
        index = y * self.width + x
        self.data[index] = value
    
    def to_image(self):
        image = pyglet.image.create(self.width, self.height)
        data_str = ""
        for col in self.data:
            rgba = color.get_rgba(col)
            data_str += "".join([chr(c) for c in rgba])
        image.set_data("RGBA", self.width * 4, data_str)
        return image
    
    def invert(self):
        for i, col in enumerate(self.data):
            if col == color.BLACK:
                self.data[i] = color.WHITE
            elif col == color.WHITE:
                self.data[i] = color.BLACK
            else:
                pass
    
    def get_color_match_nearest_pixel(self, x, y, choices, limit=None):
        if limit is None:
            limit = max(self.width, self.height)
            
        def get_spiral_coords(radius):
            if radius == 0:
                yield x, y
                return
            # Horizontal line above and below
            for y2 in (y - radius, y + radius):
                for x2 in xrange(x - radius, x + radius + 1):
                    yield x2, y2
            # Vertical line left and right
            for x2 in (x - radius, x + radius):
                for y2 in xrange(y - radius + 1, y + radius):
                    yield x2, y2
        
        for radius in xrange(limit):
            for x2, y2 in get_spiral_coords(radius):
                col = self[x2, y2]
                if col in choices:
                    return col


if __name__ == '__main__':
    image = pyglet.image.load("images/test.jpg")
    data = Pixmap.from_pyglet_image(image)
    image = data.to_image()
    image.save("/tmp/test.png")
