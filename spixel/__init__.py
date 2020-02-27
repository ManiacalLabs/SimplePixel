"""
`spixel` is a bare-bones, hardware agnostic LED control
framework written in the spirit of the [FastLED](http://fastled.io/)
Arduino library.

.. include:: ./docs.md
"""

from . pixels import Pixels
from . matrix import Matrix


__pdoc__ = {}
# don't auto-doc log module
__pdoc__['log'] = False
