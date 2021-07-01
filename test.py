import os
import numpy as np
import random
import zarr
from tqdm import tqdm
from timeit import default_timer as timer

from src.TiffSlide import TiffSlide
from src.image_util import show_image, compare_image


def test_load(filename, magnification, position, size):
    slide = TiffSlide(filename, magnification)
    image = slide.asarray(position[0], position[1], position[0] + size[0], position[1] + size[1])
    return image


def test_read_slide(image_filename, magnification, n=1000):
    print('Test read slide')
    slide = TiffSlide(image_filename, magnification)
    size = slide.get_size()
    width = size[0]
    height = size[1]
    nx = int(np.ceil(width / patch_size[0]))
    ny = int(np.ceil(height / patch_size[1]))

    slide.load()
    start = timer()
    for _ in tqdm(range(n)):
        xi = random.randrange(nx)
        yi = random.randrange(ny)
        x = xi * patch_size[0]
        y = yi * patch_size[1]
        image = slide.asarray(x, y, x + patch_size[0], y + patch_size[1])
        image.shape
        #show_image(image)
    elapsed = timer() - start
    print(f'time (total/step): {elapsed:.3f} / {elapsed / n:.3f}')


def load_zarr_test(image_filename):
    zarr_filename = os.path.splitext(image_filename)[0] + '.zarr'
    zarr_root = zarr.open_group(zarr_filename, mode='r')
    zarr_data = zarr_root.get(str(0))

    patchx = 200
    patchy = 200
    ys = patchy * patch_size[1]
    ye = ys + patch_size[1]
    xs = patchx * patch_size[0]
    xe = xs + patch_size[0]
    tile = zarr_data[ys:ye, xs:xe]
    show_image(tile)
    return tile


def test_read_zarr(image_filename, n=1000):
    print('Test read zarr')
    zarr_filename = os.path.splitext(image_filename)[0] + '.zarr'
    zarr_root = zarr.open_group(zarr_filename, mode='r')
    zarr_data = zarr_root.get(str(0))
    shape = zarr_data.shape
    width = shape[1]
    height = shape[0]
    nx = int(np.ceil(width / patch_size[0]))
    ny = int(np.ceil(height / patch_size[1]))

    for _ in tqdm(range(n)):
        xi = random.randrange(nx)
        yi = random.randrange(ny)
        xs = xi * patch_size[0]
        ys = yi * patch_size[1]
        xe = xs + patch_size[0]
        ye = ys + patch_size[1]
        tile = zarr_data[ys:ye, xs:xe]


if __name__ == '__main__':
    image_dir = 'resources/images/'
    #filename = os.path.join(image_dir, "test.svs")
    filename_svs = os.path.join(image_dir, '4c88d448-6264-4d4b-9c4e-b04da3f65841/TCGA-69-7765-01Z-00-DX1.ac389366-febb-488c-9190-fe00bc07cd20.svs')
    filename_tiff = os.path.join(image_dir, '4c88d448-6264-4d4b-9c4e-b04da3f65841/TCGA-69-7765-01Z-00-DX1.ac389366-febb-488c-9190-fe00bc07cd20.tiff')
    magnification = 20
    patch_size = (299, 299)

    #image = test_load(filename, magnification, [0, 0], [1000, 1000])
    #plt.imshow(image)
    #plt.show()

    test_read_slide(filename_tiff, magnification)

    #position = (500 * magnification, 500 * magnification)
    #image_svs = test_load(filename_svs, magnification, position, patch_size)
    #image_tiff = test_load(filename_tiff, magnification, position, patch_size)
    #show_image(image_svs)
    #show_image(image_tiff)
    #dif = compare_image(image_svs, image_tiff)
