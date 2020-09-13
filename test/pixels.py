from time import sleep
from spixel.drivers.SimPixel import SimPixel
from spixel.drivers.serial import Serial, LEDTYPE
from spixel import Pixels
from spixel import colors


def make_strip_coord_map_positions(num):
    return [[x, 0, 0] for x in range(num)]


NUM = 25

with Serial(LEDTYPE.WS2801) as d:
    pixels = Pixels(d, NUM)
    d.set_master_brightness(32)

    try:
        while True:
            pixels.clear()
            for i in range(NUM):
                pixels[i] = colors.Red
            d.update()
            sleep(1)

            pixels.clear()
            for i in range(NUM):
                pixels[i] = colors.Green
            d.update()
            sleep(1)

            pixels.clear()
            for i in range(NUM):
                pixels[i] = colors.Blue
            d.update()
            sleep(1)

            pixels.clear()
            for i in range(NUM):
                pixels[i] = colors.White
            d.update()
            sleep(1)

            for s in range(0, 256):
                pixels.clear()
                for i in range(NUM):
                    pixels.set(i, colors.hue_rainbow[s])
                d.update()
                sleep(0.01)

    except KeyboardInterrupt:
        pixels.clear()
        d.update()
        sleep(1)
