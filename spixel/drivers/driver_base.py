import time


class ChannelOrder:
    """Named color channel order enumeration. Use with `c_order` on drivers."""
    RGB = [0, 1, 2]
    RBG = [0, 2, 1]
    GRB = [1, 0, 2]
    GBR = [1, 2, 0]
    BRG = [2, 0, 1]
    BGR = [2, 1, 0]


class DriverBase(object):
    """Base driver class on which to derive other drivers.

    `c_order`: `ChannelOrder` instance to define color channel order if not `RGB`

    `gamma`: Gamma correction table (List of 256 values 0-255)
    """

    def __init__(self, c_order=ChannelOrder.RGB, gamma=None):
        self.gamma = gamma or range(256)
        self.c_order = c_order

        self.pixels = None
        """Reference to instance of `spixel.pixels.Pixels`"""
        self.num = None
        """Number of total pixels available"""
        self.buf_byte_count = None
        """Total number of bytes in pixel buffer"""
        self._buf = None

    def setup(self, pixels):
        """Called automatically by `spixel.pixels.Pixels` instance.

        `pixels`: Instance of `spixel.pixels.Pixels`
        or derived, such as `spixel.matrix.Matrix`.
        """
        self.pixels = pixels
        self.num = self.pixels.num

        self.buf_byte_count = int(3 * self.num)
        self._buf = [0] * self.buf_byte_count

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def _update(self, data):
        pass  # must be overriden by parent driver

    def update(self):
        """Call to push data to interface.
        Will call derived class `_update` function with current buffer.

        In most cases you should call `spixel.pixels.Pixels.update()` instead of calling this directly.
        """
        self._update(self.pixels.buffer)

    def set_master_brightness(self, brightness):
        """Set master max brightness value. Must be implemented by derived class."""
        return False

    def set_pixel_positions(self, pixel_positions):
        """
        **Internal Use Only**:
        Placeholder callback for sending physical pixel layout data to the
        `spixel.drivers.SimPixel` driver.
        """
        pass

    def fix_data(self, data):
        """Helper function to apply gamma correction,
        fix channel order, and load into `self._buf`.
        Can be called by derived drivers inside `_update` implementation.
        """
        gamma = self.gamma
        for a, b in enumerate(self.c_order):
            self._buf[a:self.num * 3:3] = [gamma[v] for v in data[b::3]]


__pdoc__ = {}
__pdoc__['ChannelOrder.RGB'] = ''
__pdoc__['ChannelOrder.RBG'] = ''
__pdoc__['ChannelOrder.GRB'] = ''
__pdoc__['ChannelOrder.GBR'] = ''
__pdoc__['ChannelOrder.BRG'] = ''
__pdoc__['ChannelOrder.BGR'] = ''
