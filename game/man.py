import pyglet
import random

import color
import geometry

LEFT = "LEFT"
RIGHT = "RIGHT"


class Man(object):
    def __init__(self, col):
        self.color = col
        if self.color == color.BLACK:
            image = pyglet.image.load("images/man.png")
        else:
            image = color.get_inverted(pyglet.image.load("images/man.png"))
        
        self.height = image.height
        self.width = image.width // 2
        seq = pyglet.image.ImageGrid(image, 1, 2)
        dur = random.uniform(0.2, 0.3)
        anim = pyglet.image.Animation.from_image_sequence(seq, dur, True)
        self.sprite = pyglet.sprite.Sprite(anim)

        self.pos = 0, 0
        self.direction = random.choice([LEFT, RIGHT])

        # # paths_for_colors = {BLACK: "images/man_black.png",
        # #                     WHITE: "images/man_white.png"}
        # self.sprites = {}
        # for col, path in paths_for_colors.items():
        #     image = pyglet.image.load(path)
        #     self.height = image.height
        #     self.width = image.width // 2
        #     seq = pyglet.image.ImageGrid(image, 1, 2)
        #     dur = random.uniform(0.2, 0.3)
        #     anim = pyglet.image.Animation.from_image_sequence(seq, dur, True)
        #     self.sprites[color] = pyglet.sprite.Sprite(anim)
    
    def draw(self):
        self.sprite.x, self.sprite.y = self.pos
        self.sprite.draw()


def get_mans_from_image(image):
    # rgb_data = image.get_image_data().get_data("RGB", image.width * 3)
        
    def get_green_pixels():
        for y in xrange(image.height):
            for x in xrange(image.width):
                col = color.get_color(image, x, y)
                if not col == color.GREEN:
                    continue
                yield x, y
    man_rects = geometry.get_rects_containing_points(get_green_pixels(),
                                                     threshold=8)
    
    # Create a man for each rectangle on the map. Color is based on the
    # surrounding pixels.
    for man_rect in man_rects:
        
        # Get color from background.
        x = int(man_rect.center.x)
        y = int(man_rect.center.y)
        bg_col = color.get_color_match_nearest_pixel(x, y,
                                                     (color.BLACK, color.WHITE))
        man_col = color.BLACK if bg_col == color.WHITE else color.WHITE
        
        the_man = Man(man_col)
        
        # Drop the man to the floor
        man_pos = int(man_rect.center.x), int(man_rect.center.y)
        while True:
            # Sample below
            x = man_pos[0] + the_man.width // 2
            y = man_pos[1] - 1
            if color.get_color(image, x, y) == man_col:
                break
            man_pos = man_pos[0], man_pos[1] - 1
            if man_pos <= 0:
                break
        
        the_man.pos = man_pos
    
    # # Get image for each man rect
    # for man_rect in man_rects:
    #     man_image_data = ""
    #     for y in xrange(man_rect.y, man_rect.y + man_rect.height):
    #         for x in xrange(man_rect.x, man_rect.x + man_rect.width):
    #             r, g, b = get_col(x, y)
    #             # print x, y, r, g, b
    #             if is_green(r, g, b):
    #                 man_image_data += chr(0) * 3 + chr(255)
    #             else:
    #                 man_image_data += chr(255) * 3 + chr(255)
    #     man_image = pyglet.image.create(man_rect.width, man_rect.height)
    #     man_image.set_data('RGBA', man_rect.width * 4, man_image_data)
    
