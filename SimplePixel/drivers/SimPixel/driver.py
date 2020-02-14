import struct, webbrowser
from . import websocket
from .. server_driver import ServerDriver

DEFAULT_SIMPIXEL_URL = 'http://simpixel.io'


class SimPixelOpenerServer(websocket.Server):
    def __init__(self, port, selectInterval):
        super().__init__(port, selectInterval)
        # SimPixel.open_browser()


class SimPixel(ServerDriver):
    """
    Output a simulation of your display to your browser at http://simpixel.io
    """

    SERVER_CLASS = SimPixelOpenerServer
    SERVER_KWDS = {'selectInterval': 0.001}

    @staticmethod
    def open_browser(url=DEFAULT_SIMPIXEL_URL, new=0, autoraise=True):
        if url and not url.startswith('no'):
            webbrowser.open(url, new=new, autoraise=autoraise)

    def __init__(self, pixels, port=1337, **kwds):
        """
        Args:
            num:  number of LEDs being visualizer.
            port:  the port on which the SimPixel server is running.
            pixel_positions:  the positions of the LEDs in 3-d space.
            **kwds:  keywords passed to DriverBase.
        """
        print(kwds)
        super().__init__(pixels, address=port, **kwds)

    def _on_positions(self):
        # Flatten list of led positions.
        if self.server:
            pl = [c for p in self.pixel_positions for c in p]
            positions = bytearray(struct.pack('<%sh' % len(pl), *pl))
            self.server.update(positions=positions)

    def _update(self, data):
        if not self.server:
            raise ValueError(
                'Tried to send a packet before Layout.start() was called')
        self.server.update(pixels=data)


open_browser = SimPixel.open_browser
DriverSimPixel = SimPixel
