from time import sleep
from spixel.drivers.SimPixel import SimPixel
from spixel import Pixels
from spixel import colors


def make_strip_coord_map_positions(num):
    return [[x, 0, 0] for x in range(num)]


NUM = 16

with SimPixel() as sp:
    pixels = Pixels(sp, NUM)
    sp.set_master_brightness(255)

    try:
        while True:
            pixels.clear()
            for i in range(16):
                pixels[i] = colors.Red
            sp.update()
            sleep(1)

            pixels.clear()
            for i in range(16):
                pixels[i] = colors.Green
            sp.update()
            sleep(1)

            pixels.clear()
            for i in range(16):
                pixels[i] = colors.Blue
            sp.update()
            sleep(1)

            pixels.clear()
            for i in range(16):
                pixels[i] = colors.White
            sp.update()
            sleep(1)

            # for s in range(0, 256):
            #     pixels.clear()
            #     for i in range(16):
            #         pixels.set(i, colors.hue_rainbow[s])
            #     sp.update()
            #     sleep(0.01)

    except KeyboardInterrupt:
        # matrix.clear()
        sp.update()
        sleep(1)
