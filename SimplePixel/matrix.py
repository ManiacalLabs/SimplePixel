import math
from . import colors
from . import font
from . pixels import Pixels
from . import matrix_drawing as md


def rotate_and_flip(coord_map, rotation, flip):
    rotation = (-rotation % 360) // 90
    for _ in range(rotation):
        coord_map = list(zip(*coord_map[::-1]))

    if flip:
        coord_map = coord_map[::-1]

    return coord_map


def make_matrix_coord_map(dx, dy, serpentine=False, offset=0, rotation=0, y_flip=False):
    """Helper method to generate X,Y coordinate maps for strips"""
    result = []
    for y in range(dy):
        if not serpentine or y % 2 == 0:
            result.append([(dx * y) + x + offset for x in range(dx)])
        else:
            result.append([dx * (y + 1) - 1 - x + offset for x in range(dx)])

    result = rotate_and_flip(result, rotation, y_flip)

    return result


class Matrix(Pixels):
    def __init__(self, driver, width, height, coord_map=None):
        if not coord_map:
            coord_map = make_matrix_coord_map(width, height)
        self.map = coord_map

        super().__init__(driver, width * height)

        self.width = len(self.map)
        self.height = None
        for col in self.map:
            y = len(col)
            if self.height is None:
                self.height = y
            else:
                if y != self.height:
                    raise ValueError('All columns of coords must be the same length!')

        self.fonts = font.fonts

    def get_pixel_positions(self):
        result = [None] * self.numLEDs

        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                result[self.map[y][x]] = [x, y, 0]

        return result

    def set(self, x, y, color):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        i = self.map[y][x]
        super().set(i, color)

    def __setitem__(self, pixel, color):
        x, y = pixel
        self.set(x, y, color)

    def __getitem__(self, pixel):
        x, y = pixel
        i = self.map[y][x]
        return self.get(i)

    ##########################################################################
    # Drawing Functions
    # Lovingly borrowed from Adafruit
    # https://github.com/adafruit/Adafruit-GFX-Library/blob/master/Adafruit_GFX.cpp
    ##########################################################################

    def drawCircle(self, x0, y0, r, color=None):
        """
        Draw a circle in an RGB color, with center x0, y0 and radius r.
        """
        md.draw_circle(self.set, x0, y0, r, color)

    def fillCircle(self, x0, y0, r, color=None):
        """
        Draw a filled circle in an RGB color, with center x0, y0 and radius r.
        """
        md.fill_circle(self.set, x0, y0, r, color)

    def drawLine(self, x0, y0, x1, y1, color=None, colorFunc=None, aa=False):
        """
        Draw a between x0, y0 and x1, y1 in an RGB color.

        :param colorFunc: a function that takes an integer from x0 to x1 and
            returns a color corresponding to that point
        :param aa: if True, use Bresenham's algorithm for line drawing;
            otherwise use Xiaolin Wu's algorithm
        """
        md.draw_line(self.set, x0, y0, x1, y1, color, colorFunc, aa)

    # Bresenham's algorithm
    def bresenham_line(self, x0, y0, x1, y1, color=None, colorFunc=None):
        """
        Draw line from point x0, y0 to x1, y1 using Bresenham's algorithm.

        Will draw beyond matrix bounds.
        """
        md.bresenham_line(self.set, x0, y0, x1, y1, color, colorFunc)

    # Xiaolin Wu's Line Algorithm
    def wu_line(self, x0, y0, x1, y1, color=None, colorFunc=None):
        """
        Draw a between x0, y0 and x1, y1 in an RGB color.

        :param colorFunc: a function that takes an integer from x0 to x1 and
            returns a color corresponding to that point
        :param aa: if True, use Bresenham's algorithm for line drawing;
            otherwise use Xiaolin Wu's algorithm
        """
        md.wu_line(self.set, x0, y0, x1, y1, color, colorFunc)

    def drawRect(self, x, y, w, h, color=None, aa=False):
        """
        Draw rectangle with top-left corner at x,y, width w and height h

        :param aa: if True, use Bresenham's algorithm for line drawing;
            otherwise use Xiaolin Wu's algorithm
        """
        md.draw_rect(self.set, x, y, w, h, color, aa)

    def fillRect(self, x, y, w, h, color=None, aa=False):
        """
        Draw a solid rectangle with top-left corner at (x, y), width w and
        height h.

        :param aa: if True, use Bresenham's algorithm for line drawing;
            otherwise use Xiaolin Wu's algorithm
        """
        md.fill_rect(self.set, x, y, w, h, color, aa)

    def fillScreen(self, color=None):
        """Fill the matrix with the given RGB color"""
        md.fill_rect(self.set, 0, 0, self.width, self.height, color)

    def drawRoundRect(self, x, y, w, h, r, color=None, aa=False):
        """
        Draw a rounded rectangle with top-left corner at (x, y), width w,
        height h, and corner radius r

        :param aa: if True, use Bresenham's algorithm for line drawing;
            otherwise use Xiaolin Wu's algorithm
        """
        md.draw_round_rect(self.set, x, y, w, h, r, color, aa)

    def fillRoundRect(self, x, y, w, h, r, color=None, aa=False):
        """
        Draw a rounded rectangle with top-left corner at (x, y), width w,
        height h, and corner radius r

        :param aa: if True, use Bresenham's algorithm for line drawing;
            otherwise use Xiaolin Wu's algorithm
        """
        md.fill_round_rect(self.set, x, y, w, h, r, color, aa)

    def drawTriangle(self, x0, y0, x1, y1, x2, y2, color=None, aa=False):
        """
        Draw triangle with vertices (x0, y0), (x1, y1) and (x2, y2)

        :param aa: if True, use Bresenham's algorithm for line drawing;
            Otherwise use Xiaolin Wu's algorithm
        """
        md.draw_triangle(self.set, x0, y0, x1, y1, x2, y2, color, aa)

    def drawChar(self, x, y, c, color, bg,
                 aa=False, font=font.default_font, font_scale=1):
        """
        Draw a single character c at at (x, y) in an RGB color.
        """
        md.draw_char(self.fonts, self.set, self.width, self.height,
                     x, y, c, color, bg, aa, font, font_scale)

    def drawText(self, text, x=0, y=0, color=None,
                 bg=colors.Off, aa=False, font=font.default_font,
                 font_scale=1):
        """
        Draw a line of text starting at (x, y) in an RGB color.

        :param colorFunc: a function that takes an integer from x0 to x1 and
            returns a color corresponding to that point
        :param aa: if True, use Bresenham's algorithm for line drawing;
            otherwise use Xiaolin Wu's algorithm
        """
        md.draw_text(self.fonts, self.set, text, self.width, self.height,
                     x, y, color, bg, aa, font, font_scale)
