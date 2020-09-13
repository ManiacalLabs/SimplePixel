"""
2D Matrix abstraction around `spixel.pixels` and helper functions.
"""

import math
from . import colors
from . import font
from . pixels import Pixels


def rotate_and_flip(coord_map, rotation, flip):
    rotation = (-rotation % 360) // 90
    for _ in range(rotation):
        coord_map = list(zip(*coord_map[::-1]))

    if flip:
        coord_map = coord_map[::-1]

    return coord_map


def make_matrix_coord_map(width, height, serpentine=False, offset=0, rotation=0, y_flip=False):
    """Helper method to generate X,Y coordinate maps for mapped to 1D pixel lists

    `width (int)`: X axis dimension of matrix

    `height (int)`: Y axis dimension of matrix

    `serpentine (bool)`: Generates map in serpentine pattern instead of always restarting on left

    `offset (int)`: Starting index (for when generating multiple sub-maps)

    `rotation (0, 90, 180, 270)`: Degrees to rotate matrix map by

    `y_flip (bool)`: Flip matrix along Y axis
    """
    result = []
    for y in range(height):
        if not serpentine or y % 2 == 0:
            result.append([(width * y) + x + offset for x in range(width)])
        else:
            result.append([width * (y + 1) - 1 - x + offset for x in range(width)])

    result = rotate_and_flip(result, rotation, y_flip)

    return result


class Matrix(Pixels):
    """2D Matrix abstraction wrapper around `spixel.pixels.Pixels`
    to provide `(X,Y)` coordinate mapping. Internally the data is stored as
    a 1D `spixel.pixels.Pixels` object and `(X,Y)` coordinates are mapped
    to list indicies.

    `driver`: Instance of class derived from `spixel.drivers.driver_base.DriverBase`

    `width (int)`: X axis dimension of matrix

    `height (int)`: Y axis dimension of matrix

    `coord_map`: 2D matrix mapping `(X,Y)` coordinates to 1D indicies. Will be auto-generated with best-guess if omitted.
    """
    def __init__(self, driver, width, height, serpentine=False, rotation=0, y_flip=False, coord_map=None):
        if not coord_map:
            coord_map = make_matrix_coord_map(width, height, serpentine, 0, rotation, y_flip)
        self.map = coord_map
        """Current coordinate map object"""

        super().__init__(driver, width * height)

        self.width = len(self.map)
        """X axis dimension of matrix, for querying in animation code"""
        self.height = None
        """X axis dimension of matrix, for querying in animation code"""

        for col in self.map:
            y = len(col)
            if self.height is None:
                self.height = y
            else:
                if y != self.height:
                    raise ValueError('All columns of coords must be the same length!')

    def _get_pixel_positions(self):
        """**Internal Use**: Returns pixel_positions object for `spixel.drivers.SimPixel.driver.SimPixel`"""
        result = [None] * self.num

        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                result[self.map[y][x]] = [x, y, 0]

        return result

    def set(self, x, y, color):
        """Set pixel at given `(X,Y)` coordinates to color. Can also use the format `matrix[x, y] = colors.Red` instead of calling function.

        `x (int)`: X coordinate of pixel to set

        `y (int)`: Y coordinate of pixel to set

        `color (tuple)`: `(R,G,B)` color tuple or named value from `spixel.colors`
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        i = self.map[y][x]
        super().set(i, color)

    def get(self, x, y):
        """Get pixel color tuple at given `(X,Y)` coordinate. Can also use the format `c = matrix[x, y]` instead of calling function.

        `x (int)`: X coordinate of pixel to get

        `y (int)`: Y coordinate of pixel to get

        **returns:** `(R,G,B)` color tuple
        """
        i = self.map[y][x]
        return self.get(i)

    def __setitem__(self, pixel, color):
        x, y = pixel
        self.set(x, y, color)

    def __getitem__(self, pixel):
        x, y = pixel
        return self.get(x, y)

    ##########################################################################
    # Drawing Functions
    # Lovingly borrowed from Adafruit
    # https://github.com/adafruit/Adafruit-GFX-Library/blob/master/Adafruit_GFX.cpp
    ##########################################################################

    def draw_circle(self, x0, y0, r, color=None):
        """
        Draws a circle at point `(x0,y0)` with radius `r` of the specified RGB `color` tuple
        """
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r

        self.set(x0, y0 + r, color)
        self.set(x0, y0 - r, color)
        self.set(x0 + r, y0, color)
        self.set(x0 - r, y0, color)

        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x

            self.set(x0 + x, y0 + y, color)
            self.set(x0 - x, y0 + y, color)
            self.set(x0 + x, y0 - y, color)
            self.set(x0 - x, y0 - y, color)
            self.set(x0 + y, y0 + x, color)
            self.set(x0 - y, y0 + x, color)
            self.set(x0 + y, y0 - x, color)
            self.set(x0 - y, y0 - x, color)

    def _draw_circle_helper(self, x0, y0, r, cornername, color=None):
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r

        while x < y:
            if (f >= 0):
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            if (cornername & 0x4):
                self.set(x0 + x, y0 + y, color)
                self.set(x0 + y, y0 + x, color)

            if (cornername & 0x2):
                self.set(x0 + x, y0 - y, color)
                self.set(x0 + y, y0 - x, color)

            if (cornername & 0x8):
                self.set(x0 - y, y0 + x, color)
                self.set(x0 - x, y0 + y, color)

            if (cornername & 0x1):
                self.set(x0 - y, y0 - x, color)
                self.set(x0 - x, y0 - y, color)

    def _draw_circle_filled_helper(self, x0, y0, r, cornername, delta, color=None):
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r

        while (x < y):
            if (f >= 0):
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x

            if (cornername & 0x1):
                self._draw_fast_vline(x0 + x, y0 - y, 2 * y + 1 + delta, color)
                self._draw_fast_vline(x0 + y, y0 - x, 2 * x + 1 + delta, color)

            if (cornername & 0x2):
                self._draw_fast_vline(x0 - x, y0 - y, 2 * y + 1 + delta, color)
                self._draw_fast_vline(x0 - y, y0 - x, 2 * x + 1 + delta, color)

    def draw_circle_filled(self, x0, y0, r, color=None):
        """Draws a filled circle at point `(x0,y0)` with radius `r` of the specified RGB `color` tuple"""
        self._draw_fast_vline(x0, y0 - r, 2 * r + 1, color)
        self._draw_circle_filled_helper(x0, y0, r, 3, 0, color)

    def draw_line(self, x0, y0, x1, y1, color=None, colorFunc=None, aa=False):
        """Draw a line from `(x0,y0)` to `(x1,y1)` with specified `color` tuple.

        `aa (bool)`: If `True` draw anti-aliased line
        """
        if aa:
            self._draw_wu_line(x0, y0, x1, y1, color, colorFunc)
        else:
            self._draw_bresenham_line(x0, y0, x1, y1, color, colorFunc)

    def _draw_bresenham_line(self, x0, y0, x1, y1, color=None, colorFunc=None):
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = abs(y1 - y0)

        err = dx / 2

        if y0 < y1:
            ystep = 1
        else:
            ystep = -1

        count = 0
        for x in range(x0, x1 + 1):
            if colorFunc:
                color = colorFunc(count)
                count += 1

            if steep:
                self.set(y0, x, color)
            else:
                self.set(x, y0, color)

            err -= dy
            if err < 0:
                y0 += ystep
                err += dx

    def _draw_wu_line(self, x0, y0, x1, y1, color=None, colorFunc=None):
        funcCount = [0]  # python2 hack since nonlocal not available

        def plot(x, y, level):
            c = color
            if colorFunc:
                c = colorFunc(funcCount[0])
                funcCount[0] += 1

            c = colors.scale(color, int(255 * level))
            self.set(int(x), int(y), c)

        def ipart(x):
            return int(x)

        def fpart(x):
            return x - math.floor(x)

        def rfpart(x):
            return 1.0 - fpart(x)

        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        gradient = dy / dx

        # handle first endpoint
        xend = round(x0)
        yend = y0 + gradient * (xend - x0)
        xgap = rfpart(x0 + 0.5)
        xpxl1 = xend  # this will be used in the main loop
        ypxl1 = ipart(yend)

        if steep:
            plot(ypxl1, xpxl1, rfpart(yend) * xgap)
            plot(ypxl1 + 1, xpxl1, fpart(yend) * xgap)
        else:
            plot(xpxl1, ypxl1, rfpart(yend) * xgap)
            plot(xpxl1, ypxl1 + 1, fpart(yend) * xgap)

        # first y-intersection for the main loop
        intery = yend + gradient

        # handle second endpoint
        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = fpart(x1 + 0.5)
        xpxl2 = xend  # this will be used in the main loop
        ypxl2 = ipart(yend)

        if steep:
            plot(ypxl2, xpxl2, rfpart(yend) * xgap)
            plot(ypxl2 + 1, xpxl2, fpart(yend) * xgap)
        else:
            plot(xpxl2, ypxl2, rfpart(yend) * xgap)
            plot(xpxl2, ypxl2 + 1, fpart(yend) * xgap)

        # main loop
        for x in range(int(xpxl1 + 1), int(xpxl2)):
            if steep:
                plot(ipart(intery), x, rfpart(intery))
                plot(ipart(intery) + 1, x, fpart(intery))
            else:
                plot(x, ipart(intery), rfpart(intery))
                plot(x, ipart(intery) + 1, fpart(intery))
            intery = intery + gradient

    def _draw_fast_vline(self, x, y, h, color=None, aa=False):
        self.draw_line(x, y, x, y + h - 1, color, aa)

    def _draw_fast_hline(self, x, y, w, color=None, aa=False):
        self.draw_line(x, y, x + w - 1, y, color, aa)

    def draw_rect(self, x, y, w, h, color=None):
        """Draw rectangle with top-left corner at `(x,y)`, width `w` and height `h` with specified `color` tuple"""
        self._draw_fast_hline(x, y, w, color)
        self._draw_fast_hline(x, y + h - 1, w, color)
        self._draw_fast_vline(x, y, h, color)
        self._draw_fast_vline(x + w - 1, y, h, color)

    def draw_rect_filled(self, x, y, w, h, color=None, aa=False):
        """Draw rectangle with top-left corner at `(x,y)`, width `w` and height `h` with specified `color` tuple"""
        for i in range(x, x + w):
            self._draw_fast_vline(i, y, h, color, aa)

    def draw_round_rect(self, x, y, w, h, r, color=None, aa=False):
        """Draw rectangle with top-left corner at `(x,y)`, width `w`, height `h` and corner radius `r` with specified `color` tuple"""
        self._draw_fast_hline(x + r, y, w - 2 * r, color, aa)  # Top
        self._draw_fast_hline(x + r, y + h - 1, w - 2 * r, color, aa)  # Bottom
        self._draw_fast_vline(x, y + r, h - 2 * r, color, aa)  # Left
        self._draw_fast_vline(x + w - 1, y + r, h - 2 * r, color, aa)  # Right
        # draw four corners
        self._draw_circle_helper(x + r, y + r, r, 1, color)
        self._draw_circle_helper(x + w - r - 1, y + r, r, 2, color)
        self._draw_circle_helper(x + w - r - 1, y + h - r - 1, r, 4, color)
        self._draw_circle_helper(x + r, y + h - r - 1, r, 8, color)

    def draw_round_rect_filled(self, x, y, w, h, r, color=None, aa=False):
        """Draw filled rectangle with top-left corner at `(x,y)`, width `w`, height `h` and corner radius `r` with specified `color` tuple"""
        self.draw_rect_filled(x + r, y, w - 2 * r, h, color, aa)
        self._draw_circle_filled_helper(x + w - r - 1, y + r, r,
                                        1, h - 2 * r - 1, color)
        self._draw_circle_filled_helper(x + r, y + r, r, 2, h - 2 * r - 1, color)

    def draw_triangle(self, x0, y0, x1, y1, x2, y2, color=None, aa=False):
        """Draw triangle with points `(x0,y0)`, `(x1,y1)`, and `(x2,y2)` and specified `color` tuple.

        `aa (bool)`: If `True` draw anti-aliased lines
        """
        self.draw_line(x0, y0, x1, y1, color, None, aa)
        self.draw_line(x1, y1, x2, y2, color, None, aa)
        self.draw_line(x2, y2, x0, y0, color, None, aa)

    def draw_char(self, x, y, c, color, bg, aa=False, font_name=font.default_font, font_scale=1):
        """Draw a text character `c` with top-left corner placed at `(x,y)` in specified `color`

        `bg (tuple)`: `(R,G,B)` color tuple or named value from `spixel.colors` to use as background

        `aa (bool)`: If `True` draw anti-aliased

        `font_name`: Name of font from `spixel.font.fonts`

        `font_scale (int)`: Scale factor to multiple font size by
        """
        assert font_scale >= 1, "font_scale must be >= 1"
        f = font.fonts[font_name]
        fh = f['height']
        FONT = f['data']

        c = ord(c)  # make it the int value
        if c < f['bounds'][0] or c > f['bounds'][1]:
            c_data = f['undef']
        else:
            c_data = FONT[c - f['bounds'][0]]

        fw = len(c_data)
        for i in range(fw + f['sep']):
            xPos = x + (i * font_scale)
            if ((xPos < self.width) and (xPos + fw * font_scale - 1) >= 0):
                if i >= fw:
                    line = 0
                else:
                    line = FONT[c][i]
                for j in range(fh):
                    yPos = y + (j * font_scale)
                    if ((yPos < self.height) and
                            (yPos + fh * font_scale - 1) >= 0):
                        if line & 0x1:
                            if font_scale == 1:
                                self.set(xPos, yPos, color)
                            else:
                                self.draw_rect_filled(xPos, yPos, font_scale, font_scale, color, aa)
                        elif bg != color and bg is not None:
                            if font_scale == 1:
                                self.set(xPos, yPos, bg)
                            else:
                                self.draw_rect_filled(xPos, yPos, font_scale, font_scale, bg, aa)
                    line >>= 1
        return fw + f['sep']

    def draw_text(self, text, x=0, y=0,
                  color=None, bg=colors.Off, aa=False,
                  font_name=font.default_font, font_scale=1):
        """Draw a text string `text` with top-left corner placed at `(x,y)` in specified `color`

        `bg (tuple)`: `(R,G,B)` color tuple or named value from `spixel.colors` to use as background

        `aa (bool)`: If `True` draw anti-aliased

        `font_name`: Name of font from `spixel.font.fonts`

        `font_scale (int)`: Scale factor to multiple font size by
        """
        fh = font.fonts[font_name]['height']
        for c in text:
            if c == '\n':
                y += font_scale * fh
                x = 0
            elif c == '\r':
                pass  # skip it
            else:
                fw = self.draw_char(x, y, c, color, bg, aa, font_name, font_scale)
                x += font_scale * fw
                if x >= self.width:
                    break
