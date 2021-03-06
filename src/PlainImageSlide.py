import os
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


Image.MAX_IMAGE_PIXELS = None   # avoid DecompressionBombError (which prevents loading large images)


class PlainImageSlide:
    def __init__(self, filename, source_mag, target_mag, executor=None):
        if source_mag is None or source_mag == 0:
            raise ValueError(f'Error: Provide source magnification (in parameter file) for images without meta-data')
        if executor is not None:
            self.executor = executor
        else:
            max_workers = (os.cpu_count() or 1) + 4
            self.executor = ThreadPoolExecutor(max_workers)
        self.loaded = False
        self.data = None
        self.arrays = []
        self.image = Image.open(filename)
        self.size = (self.image.width, self.image.height)
        self.source_mag = source_mag
        self.mag_factor = source_mag / target_mag

    def load(self):
        self.unload()
        self.arrays.append(np.array(self.image))
        self.loaded = True

    def unload(self):
        for array in self.arrays:
            del array
        self.arrays = []
        self.loaded = False

    def get_size(self):
        # size at selected magnification
        return np.divide(self.size, self.mag_factor)

    def get_thumbnail(self, size):
        thumb = self.image.copy()
        thumb.thumbnail(size, Image.ANTIALIAS)
        return thumb

    def asarray(self, x0, y0, x1, y1):
        # ensure fixed patch size
        w0 = x1 - x0
        h0 = y1 - y0
        if self.mag_factor != 1:
            ox0, oy0 = int(round(x0 * self.mag_factor)), int(round(y0 * self.mag_factor))
            ox1, oy1 = int(round(x1 * self.mag_factor)), int(round(y1 * self.mag_factor))
        else:
            ox0, oy0, ox1, oy1 = x0, y0, x1, y1
        image0 = self.asarray_level(0, ox0, oy0, ox1, oy1)
        if self.mag_factor != 1:
            w = int(round(image0.shape[1] / self.mag_factor))
            h = int(round(image0.shape[0] / self.mag_factor))
            pil_image = Image.fromarray(image0).resize((w, h))
            image = np.array(pil_image)
        else:
            image = image0
        w = image.shape[1]
        h = image.shape[0]
        if (h, w) != (h0, w0):
            image = np.pad(image, ((0, h0 - h), (0, w0 - w), (0, 0)), 'edge')
        return image

    def asarray_level(self, level, x0, y0, x1, y1):
        if self.loaded:
            array = self.arrays[level]
        else:
            array = np.array(self.image)
        return array[y0:y1, x0:x1]

    def get_max_mag(self):
        return self.source_mag
