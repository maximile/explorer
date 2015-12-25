import sys
import colorsys

TRANSPARENT = 0
BLACK = 1
WHITE = 2
GRAY = 3
RED = 4
BLUE = 5
GREEN = 6
YELLOW = 7
ORANGE = 8
BROWN = 9
PURPLE = 10
PINK = 11

COLORS = (TRANSPARENT, BLACK, WHITE, GRAY, RED, BLUE, GREEN, YELLOW, ORANGE,
          BROWN, PURPLE, PINK)

RGBA_FOR_COLORS = {
    TRANSPARENT: (0, 0, 0, 0),
    BLACK: (0, 0, 0, 255),
    WHITE: (255, 255, 255, 255),
    GRAY: (127, 127, 127, 255),
    RED: (173, 35, 35, 255),
    BLUE: (42, 75, 215, 255),
    GREEN: (29, 105, 20, 255),
    YELLOW: (255, 238, 51, 255),
    ORANGE: (255, 146, 51, 255),
    BROWN: (129, 74, 25, 255),
    PURPLE: (129, 38, 192, 255),
    PINK: (255, 205, 243, 255),
}

HSV_FOR_COLORS = {}
for col, rgba in RGBA_FOR_COLORS.items():
    if rgba[-1] < 127:
        continue
    rgb = [c / 255.0 for c in rgba[:3]]
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    HSV_FOR_COLORS[col] = h, s, v

# TRANSPARENT = 0
# WHITE = 1
# BLACK = 2
# RED = 3
# GREEN = 4
# BLUE = 5
# YELLOW = 6
# MAGENTA = 7
# CYAN = 8
# COLORS = [TRANSPARENT, WHITE, BLACK, RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN]

# LEVELS_FOR_COLORS = {
#     WHITE: (1, 1, 1, 1),
#     BLACK: (0, 0, 0, 1),
#     RED: (1, 0, 0, 1),
#     GREEN: (0, 1, 0, 1),
#     BLUE: (0, 0, 1, 1),
#     YELLOW: (1, 1, 0, 1),
#     MAGENTA: (1, 0, 1, 1),
#     CYAN: (0, 1, 1, 1),
#     TRANSPARENT: (0, 0, 0, 0)
# }

def get_color_for_rgba(r, g, b, a):
    if a < 127:
        return TRANSPARENT
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    
    min_diff = sys.float_info.max
    for col, hsv in HSV_FOR_COLORS.items():
        h2, s2, v2 = hsv
        diff = (h - h2) ** 2 + (s - s2) ** 2 + (v - v2) ** 2
        if diff < min_diff:
            min_diff = diff
            min_diff_col = col
    return min_diff_col


def get_rgba(col):
    return RGBA_FOR_COLORS[col]
    
#     def _get_
    
#     def __getitem__(self)
    
#     def get_color(self, x, y):
#         if x >= self.width:
#             raise IndexError(x)
#         if y >= self.height:
#             raise IndexError(y)
#         r = ord(self.data[y * self.width * 4 + x * 4])
#         g = ord(self.data[y * self.width * 4 + x * 4 + 1])
#         b = ord(self.data[y * self.width * 4 + x * 4 + 2])
#         a = ord(self.data[y * self.width * 4 + x * 4 + 3])
#         if a < 127:
#             return TRANSPARENT
#         high_low = [((c + 127) // 255) for c in (r, g, b)]
#         return tuple(high_low)
    
#     def get_image(self):
#         image = pyglet.image.create(self.width, self.height)
#         image.set_data('RGBA', image.width * 4, new_image_data)
        

# def get_inverted(image):
    
#     def get_inverse_col(col):
#         if col == WHITE:
#             return BLACK
#         elif col == BLACK:
#             return WHITE
#         elif col == TRANSPARENT:
#             return TRANSPARENT
#         else:
#             raise ValueError("Can only invert b+w images.")
    
#     def get_chars(col):
#         return "".join([chr(c) for c in col])
    
#     new_image_data = ""
#     for y in xrange(image.height):
#         for x in xrange(image.width):
#             old_col = get_color(image, x, y)
#             new_col = get_inverse_col(old_col)
#             new_image_data += get_chars(new_col)
    
#     new_image = pyglet.image.create(image.width, image.height)
#     new_image.set_data('RGBA', image.width * 4, new_image_data)
#     return new_image
            

# def get_color(x, y, data, format, pitch=None):
#     if pitch is None:
#         pitch = len(format)
#     if not format == "RGBA":
#         raise NotImplementedError()
    
#     if x >= image.width:
#         raise IndexError(x)
#     if y >= image.height:
#         raise IndexError(y)
#     r = ord(data[y * image.width * 4 + x * 4])
#     g = ord(data[y * image.width * 4 + x * 4 + 1])
#     b = ord(data[y * image.width * 4 + x * 4 + 2])
#     a = ord(data[y * image.width * 4 + x * 4 + 3])
#     if a < 127:
#         return TRANSPARENT
#     high_low = [((c + 127) // 255) for c in (r, g, b)]
#     return tuple(high_low)


# def get_color_match_nearest_pixel(image, x, y, choices, limit=None):
#     if limit is None:
#         limit = max(image.width, image.height)
        
#     def get_spiral_coords(radius):
#         if radius == 0:
#             yield x, y
#             return
#         # Horizontal line above and below
#         for y2 in (y - radius, y + radius):
#             for x2 in xrange(x - radius, x + radius + 1):
#                 yield x2, y2
#         # Vertical line left and right
#         for x2 in (x - radius, x + radius):
#             for y2 in xrange(y - radius + 1, y + radius):
#                 yield x2, y2
    
#     for radius in xrange(limit):
#         for x2, y2 in get_spiral_coords(radius):
#             col = get_color(image, x2, y2)
#             if col in choices:
#                 return col
