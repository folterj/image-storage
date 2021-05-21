import os
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from numcodecs.abc import Codec
from numcodecs.compat import ensure_ndarray
from imagecodecs import jpeg2k_encode, jpeg2k_decode


def load_image(filename):
    cv_image = cv.imread(filename)
    image = cv.cvtColor(cv_image, cv.COLOR_BGR2RGB)
    return image


def save_image(filename, image):
    cv_image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
    path = os.path.dirname(filename)
    if not os.path.exists(path):
        os.makedirs(path)
    cv.imwrite(filename, cv_image)


def show_image(image):
    # convert from bgr or grayscale:
    #thumb = cv.cvtColor(thumb, cv.COLOR_BGR2RGB)
    #thumb = cv.cvtColor(thumb, cv.COLOR_GRAY2RGB)
    plt.imshow(image)
    plt.show()


def show_image_gray(image):
    # convert from bgr or grayscale:
    #thumb = cv.cvtColor(thumb, cv.COLOR_BGR2RGB)
    #thumb = cv.cvtColor(thumb, cv.COLOR_GRAY2RGB)
    plt.imshow(image, cmap='gray')
    plt.show()


class JPEG2000(Codec):
    codec_id = "JPEG2000"

    def __init__(self, level=None):
        self.level = level

    def encode(self, buf):
        if self.level is not None:
            return jpeg2k_encode(ensure_ndarray(buf), level=self.level)
        else:
            return jpeg2k_encode(ensure_ndarray(buf))

    def decode(self, buf):
        return jpeg2k_decode(ensure_ndarray(buf))


class YUV(Codec):
    codec_id = "YUV"

    def encode(self, buf):
        buf = ensure_ndarray(buf)
        buf = cv.cvtColor(buf, cv.COLOR_RGB2YUV)
        return buf

    def decode(self, buf):
        buf = ensure_ndarray(buf)
        buf = cv.cvtColor(buf, cv.COLOR_YUV2RGB)
        return buf


class YUV422(Codec):
    codec_id = "YUV422"

    def encode(self, buf):
        buf = ensure_ndarray(buf)
        buf = np.pad(buf, ((0, 1), (0, 1), (0, 0)), 'edge')     # YUV422 and YUV420 require even sizes
        buf = rgb_to_yuv422(buf)
        return buf

    def decode(self, buf):
        buf = ensure_ndarray(buf)
        buf = buf.reshape(300, 600)
        buf = yuv422_to_rgb(buf)
        buf = buf[0:-1, 0:-1]
        return buf


class YUV420(Codec):
    codec_id = "YUV420"

    def encode(self, buf):
        buf = ensure_ndarray(buf)
        buf = np.pad(buf, ((0, 1), (0, 1), (0, 0)), 'edge')     # YUV422 and YUV420 require even sizes
        buf = cv.cvtColor(buf, cv.COLOR_RGB2YUV_I420)
        return buf

    def decode(self, buf):
        buf = ensure_ndarray(buf)
        buf = buf.reshape(450, 300)
        buf = cv.cvtColor(buf, cv.COLOR_YUV2RGB_I420)
        buf = buf[0:-1, 0:-1]
        return buf


def rgb_to_yuv422(rgb):
    yuv444 = cv.cvtColor(rgb, cv.COLOR_RGB2YUV)
    height = yuv444.shape[0]
    width = yuv444.shape[1]
    stride = width * 2
    yuv422 = np.zeros((height, stride), dtype=yuv444.dtype)
    for y in range(height):
        for x in range(0, width, 2):
            x2 = x * 2
            yuv1 = yuv444[y, x]
            yuv2 = yuv444[y, x + 1]
            yuv422[y, x2] = yuv1[0]
            yuv422[y, x2 + 1] = (int(yuv1[1]) + int(yuv2[1])) / 2
            yuv422[y, x2 + 2] = yuv2[0]
            yuv422[y, x2 + 3] = (int(yuv1[2]) + int(yuv2[2])) / 2
    return yuv422


def yuv422_to_rgb(yuv422):
    height = yuv422.shape[0]
    width = yuv422.shape[1]
    yuv444 = np.zeros((height, int(width / 2), 3), dtype=yuv422.dtype)
    for y in range(height):
        for x in range(0, width, 4):
            x2 = int(x / 2)
            y1 = yuv422[y, x]
            u = yuv422[y, x + 1]
            y2 = yuv422[y, x + 2]
            v = yuv422[y, x + 3]
            yuv444[y, x2, 0] = y1
            yuv444[y, x2, 1] = u
            yuv444[y, x2, 2] = v
            x2 += 1
            yuv444[y, x2, 0] = y2
            yuv444[y, x2, 1] = u
            yuv444[y, x2, 2] = v
    rgb = cv.cvtColor(yuv444, cv.COLOR_YUV2RGB)
    return rgb


def compare_image(image0, image1):
    dif = abs(image1.astype(np.int32) - image0.astype(np.int32)).astype(np.uint8)
    rgb_dif = np.linalg.norm(np.resize(dif, (int(dif.size / 3), 3)), axis=1)
    print(f'rgb dist max: {np.max(rgb_dif):.1f} mean: {np.mean(rgb_dif):.3f}')
    show_image(dif)
    show_image((dif * 10).astype(np.uint8))
    return dif
