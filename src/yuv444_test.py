import numpy as np


# Strutz et al 2015 - Reversible Colour Spaces without Increased Bit Depth and Their Adaptive Selection
# https://doi.org/10.1109/LSP.2015.2397034


def rgb_to_yuv(rgb):
    width, height, _ = rgb.shape
    yuv = np.zeros_like(rgb)
    for x0 in range(width):
        for y0 in range(height):
            (r, g, b) = rgb[y0, x0]
            y = round((r + 2 * g + b) / 4)
            v = r - g
            u = b - g
            yuv[y0, x0] = [int(y), int(u), int(v)]
    return yuv


def yuv_to_rgb(yuv):
    yuv = yuv.reshape(300, 300, 3)

    width, height, _ = yuv.shape
    rgb = np.zeros_like(yuv)
    for x0 in range(width):
        for y0 in range(height):
            (y, u, v) = yuv[y0, x0]
            # if u > 192:
            #     u1 = 256 - u
            # else:
            #     u1 = u
            # if v > 192:
            #     v1 = 256 - v
            # else:
            #     v1 = v
            g = y - round((u + v) / 4)
            r = v + g
            #if r > 255:
            #    r = 255
            b = u + g
            rgb[y0, x0] = [int(r), int(g), int(b)]
    return rgb


def modulo1(x):
    return modulo(x, -128, 127)


def modulo2(x):
    return modulo(x, 0, 255)


def modulo(x, l, u):
    if x > u:
        return x - 255
    elif x < l:
        return x + 255
    else:
        return x
