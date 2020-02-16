from time import sleep
from SimplePixel.drivers.SimPixel import SimPixel
from SimplePixel.pixels import Pixels
from SimplePixel.matrix import Matrix
from SimplePixel import colors

W = 8
H = 8
NUM = W*H

with SimPixel(NUM) as sp:
    m = Matrix(sp, W, H)
    sp.setMasterBrightness(255)

    hue_map = colors.diagonal_matrix(16)[::-1]

    try:
        while True:
            for step in range(256):
                for x in range(W):
                    for y in range(H):
                        c = colors.hue2rgb((hue_map[y][x] + step) % 255)
                        m.set(x, y, c)
                sp.update()
                sleep(0.01)

    except KeyboardInterrupt:
        m.clear()
        sp.update()
        sleep(1)
