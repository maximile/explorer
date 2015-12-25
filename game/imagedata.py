import array
import pyglet

import color


class ImageData(object):
    @classmethod
    def from_pyglet_image(cls, image):
        def _get_colors_for_image():
            data_str = image.get_data("RGBA", image.width * 4)
            for i in xrange(image.width * image.height):
                r = ord(data_str[i * 4])
                g = ord(data_str[i * 4 + 1])
                b = ord(data_str[i * 4 + 2])
                a = ord(data_str[i * 4 + 3])
                yield color.get_color_for_rgba(r, g, b, a)

        data = array.array("B", _get_colors_for_image())
        return ImageData(image.width, image.height, data)
    
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


if __name__ == '__main__':
    image = pyglet.image.load("images/test.png")
    data = ImageData.from_pyglet_image(image)
    image = data.to_image()
    image.save("/tmp/test.png")
