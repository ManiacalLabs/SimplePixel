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

    def draw_circle(self, x0, y0, r, color=None):
        """
        Draws a circle at point x0, y0 with radius r of the specified RGB color
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

    def _fill_circle_helper(self, x0, y0, r, cornername, delta, color=None):
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

    def fill_circle(self, x0, y0, r, color=None):
        """Draws a filled circle at point x0,y0 with radius r and specified color"""
        self._draw_fast_vline(x0, y0 - r, 2 * r + 1, color)
        self._fill_circle_helper(x0, y0, r, 3, 0, color)

    def draw_line(self, x0, y0, x1, y1, color=None, colorFunc=None, aa=False):
        if aa:
            self.wu_line(x0, y0, x1, y1, color, colorFunc)
        else:
            self.bresenham_line(x0, y0, x1, y1, color, colorFunc)

    def bresenham_line(self, x0, y0, x1, y1, color=None, colorFunc=None):
        """Draw line from point x0,y0 to x,1,y1. Will draw beyond matrix bounds."""
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

    def wu_line(self, x0, y0, x1, y1, color=None, colorFunc=None):
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

    def draw_rect(self, x, y, w, h, color=None, aa=False):
        """Draw rectangle with top-left corner at x,y, width w and height h"""
        self._draw_fast_hline(x, y, w, color, aa)
        self._draw_fast_hline(x, y + h - 1, w, color, aa)
        self._draw_fast_vline(x, y, h, color, aa)
        self._draw_fast_vline(x + w - 1, y, h, color, aa)

    def fill_rect(self, x, y, w, h, color=None, aa=False):
        """Draw solid rectangle with top-left corner at x,y, width w and height h"""
        for i in range(x, x + w):
            self._draw_fast_vline(i, y, h, color, aa)

    def draw_round_rect(self, x, y, w, h, r, color=None, aa=False):
        """Draw rectangle with top-left corner at x,y, width w, height h,
        and corner radius r.
        """
        self._draw_fast_hline(x + r, y, w - 2 * r, color, aa)  # Top
        self._draw_fast_hline(x + r, y + h - 1, w - 2 * r, color, aa)  # Bottom
        self._draw_fast_vline(x, y + r, h - 2 * r, color, aa)  # Left
        self._draw_fast_vline(x + w - 1, y + r, h - 2 * r, color, aa)  # Right
        # draw four corners
        self._draw_circle_helper(x + r, y + r, r, 1, color)
        self._draw_circle_helper(x + w - r - 1, y + r, r, 2, color)
        self._draw_circle_helper(x + w - r - 1, y + h - r - 1, r, 4, color)
        self._draw_circle_helper(x + r, y + h - r - 1, r, 8, color)

    def fill_round_rect(self, x, y, w, h, r, color=None, aa=False):
        """Draw solid rectangle with top-left corner at x,y, width w, height h,
        and corner radius r"""
        self.fill_rect(x + r, y, w - 2 * r, h, color, aa)
        self._fill_circle_helper(x + w - r - 1, y + r, r,
                                 1, h - 2 * r - 1, color)
        self._fill_circle_helper(x + r, y + r, r, 2, h - 2 * r - 1, color)

    def draw_triangle(self, x0, y0, x1, y1, x2, y2, color=None, aa=False):
        """Draw triangle with points x0,y0 - x1,y1 - x2,y2"""
        self.draw_line(x0, y0, x1, y1, color, None, aa)
        self.draw_line(x1, y1, x2, y2, color, None, aa)
        self.draw_line(x2, y2, x0, y0, color, None, aa)

    def draw_char(self, x, y, c, color, bg, aa=False, font_name=font.default_font, font_scale=1):

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
                                self.fill_rect(xPos, yPos, font_scale, font_scale, color, aa)
                        elif bg != color and bg is not None:
                            if font_scale == 1:
                                self.set(xPos, yPos, bg)
                            else:
                                self.fill_rect(xPos, yPos, font_scale, font_scale, bg, aa)
                    line >>= 1
        return fw + f['sep']

    def draw_text(self, text, x=0, y=0,
                  color=None, bg=colors.Off, aa=False,
                  font_name=font.default_font, font_scale=1):
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
