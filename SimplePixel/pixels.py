class Pixels(object):
    def __init__(self, driver, num):
        self.driver = driver
        self.numLEDs = num
        self.buffer = None

        self.clear()

        self.driver.setup(self)
        self.driver.set_pixel_positions(self.get_pixel_positions())

    def get_pixel_positions(self):
        return [[x, 0, 0] for x in range(self.numLEDs)]

    def clear(self):
        self.buffer = [0] * (3 * self.numLEDs)

    def set(self, pixel, color):
        self.buffer[pixel * 3:(pixel * 3) + 3] = color

    def setRGB(self, pixel, r, g, b):
        self.set(pixel, (r, g, b))
