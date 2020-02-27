"""
Base, simplest object to hold and manage an abstracted pixel buffer.
"""


class Pixels(object):
    """Holds pixel data in `Pixels.buffer` as `[R,G,B,R,G,B,...]` byte data.
    This data intentionally has no channel order or color correction.
    Those must be applied by the driver.

    `driver`: Instance of class derived from `spixel.drivers.driver_base.DriverBase`

    `num (int)`: Number of pixels to be held by buffer.
    """
    def __init__(self, driver, num):
        self.driver = driver
        self.num = num
        """Number of total pixels available"""
        self.last_index = self.num - 1
        """Index of last pixel in buffer"""
        self.buffer = None
        """Holds the current pixel data as `[R,G,B,R,G,B,...]` bytes"""

        self.clear()

        self.driver.setup(self)
        self.driver.set_pixel_positions(self._get_pixel_positions())

    def update(self):
        """Pushes current buffer and forces pixel update on the driver."""
        self.driver.update()

    def _get_pixel_positions(self):
        """**Internal Use**: Returns pixel_positions object for `spixel.drivers.SimPixel.driver.SimPixel`"""
        return [[x, 0, 0] for x in range(self.num)]

    def clear(self):
        """Clear the entire buffer (set all to 'off')"""
        self.buffer = [0] * (3 * self.num)

    def set(self, pixel, color):
        """Set pixel at given index to color. Can also use the format `pixels[i] = colors.Red` instead of calling function.

        `pixel (int)`: Index of pixel to set

        `color (tuple)`: `(R,G,B)` color tuple or named value from `spixel.colors`
        """
        self.buffer[pixel * 3:(pixel * 3) + 3] = color

    def set_rgb(self, pixel, r, g, b):
        """Set pixel at given index to color using individual R, G, B values.

        `pixel (int)`: Index of pixel to set

        `r (int)`: 0-255 brightness value for Red

        `g (int)`: 0-255 brightness value for Green

        `b (int)`: 0-255 brightness value for Blue
        """
        self.set(pixel, (r, g, b))

    def get(self, pixel):
        """Get pixel color tuple at given index. Can also use the format `c = pixels[i]` instead of calling function.

        `pixel (int)`: Index of pixel to set

        **returns:** `(R,G,B)` color tuple
        """
        if pixel < 0 or pixel > self.last_index:
            return 0, 0, 0  # don't go out of bounds

        return (self.buffer[pixel * 3 + 0], self.buffer[pixel * 3 + 1], self.buffer[pixel * 3 + 2])

    def __setitem__(self, pixel, color):
        self.set(pixel, color)

    def __getitem__(self, pixel):
        return self.get(pixel)
