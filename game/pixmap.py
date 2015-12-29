import copy
import array
import pyglet

import color
import geometry


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
    
    def __copy__(self):
        raise NotImplementedError("Only supports deepcopy.")
    
    def __deepcopy__(self, memo):
        data = copy.deepcopy(self.data, memo)
        return Pixmap(self.width, self.height, data)
    
    def __iter__(self):
        for x in xrange(self.width):
            for y in xrange(self.height):
                yield x, y
    
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
    
    def flip(self):
        for y in xrange(self.height):
            row_start = y * self.width
            row_end = (y + 1) * self.width
            flipped_row = self.data[row_start:row_end]
            flipped_row.reverse()
            self.data[row_start:row_end] = flipped_row
    
    def remove_colors(self, remove=None, keep=None):
        if remove and keep:
            raise ValueError("Pass only one of remove or keep.")
        if remove:
            to_remove = remove
            to_keep = set(color.colors) - set(to_remove)
        else:
            to_keep = keep
            to_remove = set(color.COLORS) - set(keep)
        
        original = copy.deepcopy(self)
        
        for x in xrange(self.width):
            for y in xrange(self.height):
                col = self[x, y]
                if col in to_remove:
                    self[x, y] = original.get_color_match_nearest_pixel(x, y,
                                                                    to_keep)
    
    def get_sub_rects(self, col, threshold=1):
        points = [(x, y) for (x, y) in self if self[x, y] == col]
        return geometry.get_rects_containing_points(points, threshold)
        # # Start with one rect per pixel
        # rects = []
        # for x in xrange(self.width):
        #     for y in xrange(self.height):
        #         if self[x, y] == col:
        #             rects.append(x, y, 1, 1)
        
        # def rect_dist(rect_one, rect_two):
            

        # def coalesce_rects():
        #     while True:
        #         found_merge = False
        #         for i_one, rect_one in enumerate(rects):
        #             for i_two, rect_two in enumerate(rects):
        #                 if i_one == i_two:
        #                     continue
        #                 if rect_one.manhattan_distance_to_rect(rect_two) > threshold:
        #                     continue
        #                 new_rect = rect_one.union(rect_two)
        #                 found_merge = True
        #                 break
        #             if found_merge:
        #                 break
        #         if found_merge:
        #             del rects[max(i_one, i_two)]
        #             del rects[min(i_one, i_two)]
        #             rects.append(new_rect)
        #         else:
        #             return rects
            
        # while True:
        #     rects_before = rects
        #     rects = coalesce_rects(rects)
        #     if rects == rects_before:
        #         break
        
    def fill_rect(self, x, y, w, h, col, invert=False):
        def get_coords():
            for y2 in xrange(self.height):
                if y2 < y or y2 > y + h:
                    continue
                for x2 in xrange(self.width):
                    if x2 < x or x2 > x + w:
                        continue
                    yield x2, y2
        
        def get_coords_inverted():
            for y2 in xrange(self.height):
                for x2 in xrange(self.width):
                    if x <= x2 <= x + w - 1 and y <= y2 <= y + h - 1:
                        continue
                    yield x2, y2
        
        if invert:
            coords = get_coords_inverted()
        else:
            coords = get_coords()
        for x3, y3 in coords:
            self[x3, y3] = col
    
    def replace_colors(self, replacements):
        if set(replacements.keys()).intersection(set(replacements.values())):
            source = copy.deepcopy(self)
        else:
            source = self
        for x in xrange(self.width):
            for y in xrange(self.height):
                col = source[x, y]
                replacement = replacements.get(col)
                if not replacement:
                    continue
                self[x, y] = replacement
        
    def collision(self, other, other_pos=(0, 0)):
        # Check bounding box first
        if other_pos[0] >= self.width:
            return
        if other_pos[1] >= self.height:
            return
        if other_pos[0] - other.width < 0:
            return
        if other_pos[1] - other.height < 0:
            return
        
        # Check pixel by pixel
        for other_y in xrange(other.height):
            for other_x in xrange(other.height):
                self_x = other_x + other_pos[0]
                self_y = other_y + other_pos[1]
                self_col = self[self_x, self_y]
                if self_col == color.TRANSPARENT:
                    continue
                other_col = other[other_x, other_y]
                if self_col == other_col:
                    return self_x, self_y
        
        # No collision
        return None
    
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
                if not 0 <= x2 < self.width:
                    continue
                if not 0 <= y2 < self.height:
                    continue
                col = self[x2, y2]
                if col in choices:
                    return col


if __name__ == '__main__':
    image = pyglet.image.load("images/test.jpg")
    data = Pixmap.from_pyglet_image(image)
    data.to_image().save("/tmp/test_1.png")
    data.invert()
    data.to_image().save("/tmp/test_2.png")
    data.flip()
    data.to_image().save("/tmp/test_3.png")
