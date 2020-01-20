from . driver_base import DriverBase
from .. util import exception
import errno
from .. import log

class StaticCache:
    SERVER_CLASS = None
    SERVER_KWDS = {}
    CACHE = None

    @classmethod
    def cache(cls):
        if not cls.CACHE:
            cls.CACHE = ServerCache(cls.SERVER_CLASS, **cls.SERVER_KWDS)
        return cls.CACHE

    @classmethod
    def close_all(cls):
        if cls.CACHE:
            cls.CACHE.close_all()
            cls.CACHE = None


class ServerCache:
    """
    A class that caches servers by key so you don't keep closing and re-opening
    the same server and interrupting your connection.

    The exact nature of the key depends on the sort of server.
    For example, for a server socket like SimPixel, it would be just a port
    number, whereas for a UDP connection like Art-Net, it would be a
    port, ip_address pair.
    """

    def __init__(self, constructor, **kwds):
        """
        :param constructor: a function which takes a key and some keywords,
            and returns a new server
        :param kwds: keywords to the ``constructor`` function
        """
        self.servers = {}
        self.constructor = constructor
        self.kwds = kwds

    def get_server(self, key, **kwds):
        """
        Get a new or existing server for this key.

        :param int key: key for the server to use
        """
        kwds = dict(self.kwds, **kwds)
        server = self.servers.get(key)
        if server:
            # Make sure it's the right server.
            server.check_keywords(self.constructor, kwds)
        else:
            # Make a new server
            server = _CachedServer(self.constructor, key, kwds)
            self.servers[key] = server

        return server

    def close(self, key):
        server = self.servers.pop(key, None)
        if server:
            server.server.close()
            return True

    def close_all(self):
        for key in list(self.servers.keys()):
            self.close(key)


class _CachedServer:
    def __init__(self, constructor, key, kwds):
        try:
            self.server = constructor(key, **kwds)
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                e.strerror += ADDRESS_IN_USE_ERROR.format(key)
                e.args = (e.errno, e.strerror)
            raise
        self.key = key
        self.constructor = constructor
        self.kwds = kwds

    def check_keywords(self, constructor, kwds):
        if self.constructor != constructor:
            raise ValueError(CACHED_SERVER_ERROR.format(
                key=self.key,
                new_type=str(constructor),
                old_type=str(self.constructor)))

        if self.kwds != kwds:
            log.warning(CACHED_KWDS_WARNING.format(server=self, kwds=kwds))

    def close(self):
        pass

    def __getattr__(self, key):
        # Pass through all other attributes to the server.
        return getattr(self.server, key)


ADDRESS_IN_USE_ERROR = """

Cached server {0} on your machine is already in use.
Perhaps SimplePixel is already running on your machine?
"""

CACHED_SERVER_ERROR = """
Tried to open server of type {new_type} on {port}, but there was already
a server of type {old_type} running there.
"""

CACHED_KWDS_WARNING = """
Cached server for {server.port} had keywords {server.kwds},
but keywords {kwds} were requested.
"""


class ServerDriver(DriverBase, StaticCache):
    def __init__(self, pixels, address, pixel_positions=None, **kwds):
        """
        Args:
            port:  the port on which the server is running.
            pixel_positions:  the positions of the LEDs in 3-d space.
            **kwds:  keywords passed to DriverBase.
        """
        super().__init__(pixels)
        self.address = address
        self.server = self.thread = None
        self.pixel_positions = pixel_positions
        if pixel_positions:
            self.set_pixel_positions(pixel_positions)

    def start(self):
        self.server = self.cache().get_server(self.address)
        self._on_positions()

    @classmethod
    def stop_all(cls):
        cls.CACHE and cls.CACHE.close_all()

    def set_pixel_positions(self, pixel_positions):
        # This is the "automatic" update from the layout - don't overwrite
        # any pixel_position set in the constructor.
        if self.pixel_positions is None:
            self.pixel_positions = pixel_positions
            self._on_positions()

    def _send_packet(self):
        pass

    def _on_positions(self):
        pass

    def cleanup(self):
        if self.server:
            exception.report(self.server.close)
            self.server = None

    def _compute_packet(self):
        self._render()
