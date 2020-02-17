import time


class ChannelOrder:
    RGB = [0, 1, 2]
    RBG = [0, 2, 1]
    GRB = [1, 0, 2]
    GBR = [1, 2, 0]
    BRG = [2, 0, 1]
    BGR = [2, 1, 0]


class DriverBase(object):
    """Base driver class to build other drivers from"""

    def __init__(self, c_order=ChannelOrder.RGB, gamma=None):
        self.gamma = gamma or range(256)
        self.c_order = c_order

        self.lastUpdate = 0
        self.pixels = None
        self.numLEDs = None
        self.bufByteCount = None
        self._buf = None

    def setup(self, pixels):
        self.pixels = pixels
        self.numLEDs = self.pixels.numLEDs

        self.bufByteCount = int(3 * self.numLEDs)
        self._buf = [0] * self.bufByteCount

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def _update(self, data):
        pass  # must be overriden by parent driver

    def update(self):
        self._update(self.pixels.buffer)

    def setMasterBrightness(self, brightness):
        return False

    def set_pixel_positions(self, pixel_positions):
        """
        Internal Use Only

        Placeholder callback for sending physical pixel layout data to the
        ``SimPixel`` driver.
        """
        pass

    def _fixData(self, data):
        gamma = self.gamma
        for a, b in enumerate(self.c_order):
            self._buf[a:self.numLEDs * 3:3] = [gamma[v] for v in data[b::3]]
