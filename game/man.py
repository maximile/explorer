import pyglet
import random

import color
import geometry
import pixmap

LEFT = "LEFT"
RIGHT = "RIGHT"


class Man(object):
    def __init__(self, col):
        self.color = col
        image = pyglet.image.load("images/man.png")
        if self.color == color.WHITE:
            img_map = pixmap.Pixmap.from_pyglet_image(image)
            img_map.invert()
            image = img_map.to_image()
        
        self.height = image.height
        self.width = image.width // 2
        seq = pyglet.image.ImageGrid(image, 1, 2)
        dur = random.uniform(0.2, 0.3)
        anim = pyglet.image.Animation.from_image_sequence(seq, dur, True)
        self.sprite = pyglet.sprite.Sprite(anim)

        self.pos = 0, 0
        self.direction = random.choice([LEFT, RIGHT])
    
    def update(self, game, dt):
        
    
    def draw(self):
        self.sprite.x, self.sprite.y = self.pos
        self.sprite.draw()


def get_mans_from_pixmap(pix_map):
    def get_green_pixels():
        for y in xrange(pix_map.height):
            for x in xrange(pix_map.width):
                col = pix_map[x, y]
                if not col == color.GREEN:
                    continue
                yield x, y
    man_rects = geometry.get_rects_containing_points(get_green_pixels(),
                                                     threshold=8)
    
    # Create a man for each rectangle on the map. Color is based on the
    # surrounding pixels.
    mans = {}
    for i, man_rect in enumerate(man_rects):
        
        # Get color from background.
        x = int(man_rect.center.x)
        y = int(man_rect.center.y)
        bg_col = pix_map.get_color_match_nearest_pixel(x, y,
                                                     (color.BLACK, color.WHITE))
        man_col = color.BLACK if bg_col == color.WHITE else color.WHITE
        
        the_man = Man(man_col)
        mans[i] = the_man
        
        # Drop the man to the floor
        man_pos = int(man_rect.center.x), int(man_rect.center.y)
        while True:
            # Sample below
            x = man_pos[0] + the_man.width // 2
            y = man_pos[1] - 1
            if pix_map[x, y] == man_col:
                break
            man_pos = man_pos[0], man_pos[1] - 1
            if man_pos <= 0:
                break
        
        the_man.pos = man_pos
    
    return mans
