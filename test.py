import os
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

from src.TiffCacheSlide import TiffCacheSlide
from src.TiffSlide import TiffSlide


def test_load(filename, executor, position, size):
    slide = TiffSlide(filename, executor)
    image = slide.asarray(0, position[0], position[1], position[0] + size[0], position[1] + size[1])
    return image


def test_cache_load(filename, executor, position, size):
    slide = TiffCacheSlide(filename, executor)
    slide.load()
    # operations on cached slide
    image = slide.asarray(0, position[0], position[1], position[0] + size[0], position[1] + size[1])
    slide.unload()
    return image


if __name__ == '__main__':
    filename = "test.svs"
    max_workers = (os.cpu_count() or 1) + 4
    executor = ThreadPoolExecutor(max_workers)
    position = [0, 0]
    size = [1000, 1000]

    image = test_cache_load(filename, executor, position, size)
    plt.imshow(image)
    plt.show()
