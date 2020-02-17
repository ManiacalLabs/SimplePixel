class Pixels(object):
    def __init__(self, driver, num):
        self.driver = driver
        self.numLEDs = num
        self.lastIndex = self.numLEDs - 1
        self.buffer = None

        self.clear()

        self.driver.setup(self)
        self.driver.set_pixel_positions(self.get_pixel_positions())

    def update(self):
        self.driver.update()

    def get_pixel_positions(self):
        return [[x, 0, 0] for x in range(self.numLEDs)]

    def clear(self):
        self.buffer = [0] * (3 * self.numLEDs)

    def set(self, pixel, color):
        self.buffer[pixel * 3:(pixel * 3) + 3] = color

    def get(self, pixel):
        if pixel < 0 or pixel > self.lastIndex:
            return 0, 0, 0  # don't go out of bounds

        return (self.buffer[pixel * 3 + 0], self.buffer[pixel * 3 + 1], self.buffer[pixel * 3 + 2])

    def __setitem__(self, pixel, color):
        self.set(pixel, color)

    def __getitem__(self, pixel):
        return self.get(pixel)

    def setRGB(self, pixel, r, g, b):
        self.set(pixel, (r, g, b))
