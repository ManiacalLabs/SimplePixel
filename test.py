from time import sleep
from SimplePixel.drivers.SimPixel import SimPixel
from SimplePixel.pixels import Pixels
from SimplePixel.matrix import Matrix
from SimplePixel import colors


def make_strip_coord_map_positions(num):
    return [[x, 0, 0] for x in range(num)]


NUM = 16

with SimPixel(NUM) as sp:
    pixels = Pixels(sp, NUM)
    sp.setMasterBrightness(255)


    hue_map = colors.diagonal_matrix(16)[::-1]

    try:
        while True:
            # for step in range(256):
            #     for x in range(16):
            #         for y in range(16):
            #             c = colors.hue2rgb((hue_map[y][x] + step) % 255)
            #             matrix.set(x, y, c)
            #     sp.update()
            #     sleep(0.01)

            pixels.clear()
            for i in range(16):
                pixels.set(i, colors.Red)
            sp.update()
            sleep(1)

            pixels.clear()
            for i in range(16):
                pixels.set(i, colors.Green)
            sp.update()
            sleep(1)

            pixels.clear()
            for i in range(16):
                pixels.set(i, colors.Blue)
            sp.update()
            sleep(1)

            pixels.clear()
            for i in range(16):
                pixels.set(i, colors.White)
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
