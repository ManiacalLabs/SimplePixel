from time import sleep
from SimplePixel.drivers.SimPixel import SimPixel
from SimplePixel.pixels import Pixels
from SimplePixel.matrix import Matrix
from SimplePixel import colors
from SimplePixel import log

W = 32
H = 32

with SimPixel() as sp:
    m = Matrix(sp, W, H)
    sp.setMasterBrightness(255)

    hue_map = colors.diagonal_matrix(16)[::-1]

    TEST_FUNCS = [
        lambda: m.draw_circle(W//2, H//2, W//2-1, colors.Orange),
        lambda: m.fill_circle(W//2, H//2, W//2-1, colors.Orange),
        lambda: m.draw_line(0, 2, W-1, H-2, colors.Green, aa=False),
        lambda: m.draw_line(0, 2, W-1, H-2, colors.Green, aa=True),
        lambda: m.draw_rect(1, 1, W-2, H-2, colors.Purple),
        lambda: m.fill_rect(1, 1, W-2, H-2, colors.Purple),
        lambda: m.draw_round_rect(4, 4, W-5, H-5, 6, colors.Red),
        lambda: m.fill_round_rect(4, 4, W-5, H-5, 6, colors.Red),
        lambda: m.draw_triangle(4, 4, W//2, H-1, H//2, 0, colors.Blue, aa=True),
        lambda: m.draw_text('TEST', color=colors.Blue, font_scale=2)
    ]

    try:
        while True:
            for f in TEST_FUNCS:
                m.clear()
                f()
                m.update()
                sleep(1)

            # for step in range(256):
            #     for x in range(W):
            #         for y in range(H):
            #             c = colors.hue2rgb((hue_map[y][x] + step) % 255)
            #             m[x, y] = c
            #     m.update()
            #     sleep(0.01)

    except KeyboardInterrupt:
        m.clear()
        sp.update()
        sleep(1)
