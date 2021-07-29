# OME TIFF format: https://svi.nl/OMEfileFormat
# HDF5 format: https://svi.nl/HDF5

# reading: OpenSlide or PMA: https://realdata.pathomation.com/sdk-update-for-python/

# Zarr
# https://forum.image.sc/t/how-to-convert-multi-resolution-image-pyramid-data-into-a-zarr-file-so-that-it-can-be-loaded-in-napari/41804
# https://github.com/sofroniewn/image-demos/blob/4ddcfc23980e37fbe5eda8150c14af8220369f24/helpers/make_2D_zarr_pathology.py
# https://github.com/sofroniewn/image-demos/blob/4ddcfc23980e37fbe5eda8150c14af8220369f24/examples/pathology.py


import glob
import os
import bioformats
import javabridge
import numpy as np
import pandas as pd
import pyvips
import zarr
from imageio import imread
from numcodecs import register_codec
from numcodecs.blosc import Blosc
from tifffile import tifffile, TiffFile, TiffWriter
from tqdm import tqdm

from src.TiffSlide import TiffSlide
from src.image_util import JPEG2000, YUV, YUV422, YUV420, tags_to_dict, compare_image, tiff_info_short

register_codec(JPEG2000)
register_codec(YUV)
register_codec(YUV422)
register_codec(YUV420)


def convert_slides(csv_file, image_dir, patch_size):
    data = pd.read_csv(csv_file, delimiter='\t').to_dict()
    image_files = list(data['path'].values())
    nslides = len(image_files)

    for image_file in tqdm(image_files, total=nslides):
        filename = os.path.join(image_dir, image_file)
        if os.path.isfile(filename):
            convert_slide_to_zarr(filename, patch_size)


def convert_slide_to_zarr0(filename, patch_size):
    slide = TiffSlide(filename)
    size = slide.sizes[0]
    width = size[0]
    height = size[1]
    compressor = Blosc(cname='zstd', clevel=3, shuffle=Blosc.BITSHUFFLE)    # clevel=9

    zarr_filename = os.path.splitext(filename)[0] + '.zarr'
    root = zarr.open_group(zarr_filename, mode='a')

    nx = int(np.ceil(width / patch_size[0]))
    ny = int(np.ceil(height / patch_size[1]))

    # thumbnail
    level = 1
    label = str(level)
    if label not in root.array_keys():
        thumb = np.asarray(slide.get_thumbnail((nx, ny)))
        # ensure correct size in case thumb scaled using aspect ratio
        if thumb.shape[1] < nx or thumb.shape[0] < ny:
            if thumb.shape[1] < nx:
                dx = nx - thumb.shape[1]
            else:
                dx = 0
            if thumb.shape[0] < ny:
                dy = ny - thumb.shape[0]
            else:
                dy = 0
            thumb = np.pad(thumb, ((0, dy), (0, dx), (0, 0)), 'edge')
        thumb = thumb[0:ny, 0:nx]
        root.create_dataset(label, data=thumb,
                            compressor=compressor)

    # slide
    level = 0
    label = str(level)
    if label not in root.array_keys():
        data = root.create_dataset(label, shape=(height, width, 3),
                                   chunks=(patch_size[0], patch_size[1], None), dtype='uint8',
                                   compressor=compressor)
                                   #compressor=None, filters=[YUV420(), JPEG2000(50)])
        for y in range(ny):
            ys = y * patch_size[1]
            h = patch_size[1]
            if ys + h > height:
                h = height - ys
            for x in range(nx):
                xs = x * patch_size[0]
                w = patch_size[0]
                if xs + w > width:
                    w = width - xs
                tile = slide.asarray(xs, ys, xs + w, ys + h)
                data[ys:ys+h, xs:xs+w] = tile


def convert_slide_to_zarr(image_filename, patch_size):
    slide = TiffSlide(image_filename)
    size = slide.sizes[0]
    width = size[0]
    height = size[1]

    zarr_filename = os.path.splitext(image_filename)[0] + '.zarr'
    zarr_root = zarr.open_group(zarr_filename, mode='w')

    shape = (height, width, 3)
    #compressor = Blosc(cname='zstd', clevel=9, shuffle=Blosc.BITSHUFFLE)    # similar: cname='zlib'
    zarr_data = zarr_root.create_dataset(str(0), shape=shape, chunks=(patch_size[0], patch_size[1], None), dtype='uint8',
                                         compressor=None, filters=[YUV420(), JPEG2000(50)])
    return zarr_data


def convert_tiffs_tiling(folder, description):
    for filename in glob.glob(folder + "*.tiff"):
        convert_tiff_tiling(filename, description)


def convert_tiff_tiling(input_filename, description):
    tile_size = (256, 256)
    image = tifffile.imread(input_filename)[:, :, 0:3]
    path_ext = os.path.splitext(input_filename)
    output_filename = path_ext[0] + '.jpeg' + path_ext[1]
    with tifffile.TiffWriter(output_filename) as tiff:
        tiff.save(image, tile=tile_size, compression='JPEG', description=description)
        # compression=('JPEG2000', 50)


def convert_slides_tiff(input_path, input_ext, output_path, output_ext):
    for dirpath, dirs, files in os.walk(input_path):
        for file in files:
            if os.path.splitext(file)[1] == input_ext:
                filename = os.path.join(dirpath, file)
                file_ext = os.path.splitext(filename)
                outfilename = file_ext[0].replace(input_path, output_path) + output_ext
                convert_slide_tiff(filename, outfilename)


def convert_slides_tiff_select(input_path, output_path, output_ext, slidelist_filename):
    data = pd.read_csv(slidelist_filename, delimiter='\t').to_dict()
    image_files = list(data['path'].values())
    for image_file in tqdm(image_files):
        filename = os.path.join(input_path, image_file)
        file_ext = os.path.splitext(filename)
        outfilename = file_ext[0].replace(input_path, output_path) + output_ext
        convert_slide_tiff(filename, outfilename)


def convert_slide_tiff(infilename, outfilename, ome=False, overwrite=False):
    if overwrite or not os.path.exists(outfilename):
        print(f'{infilename} -> {outfilename}')
        try:
            tiff = TiffFile(infilename)
            outpath = os.path.dirname(outfilename)
            if not os.path.exists(outpath):
                os.makedirs(outpath)
            with TiffWriter(outfilename, ome=ome, bigtiff=True) as writer:
                for page in tiff.pages:
                    if page.is_tiled:
                        tile_size = (page.tilelength, page.tilewidth)
                        if ome:
                            metadata = tags_to_dict(page.tags)
                            description = None
                        else:
                            metadata = None
                            description = page.description
                        writer.write(page.asarray(), tile=tile_size, compression=['JPEG2000', 10],
                                     metadata=metadata, description=description)
        except Exception as e:
            print('file:', infilename, e)


def export_tiffwriter(filename, image, tile_size, compression):
    with TiffWriter(filename) as writer:
        writer.write(image, tile=tile_size, compression=compression)


def export_vips(filename, image, tile_size, compression):
    #numpy2vips
    image = pyvips.Image.new_from_array(image)
    image.tiffsave()
    #image.write_to_file(filename)


def export_bioformats(filename, image, tile_size, compression):
    if image.dtype == np.uint8:
        pixel_type = bioformats.PT_UINT8
    else:
        pixel_type = bioformats.PT_UINT16
    bioformats.write_image(filename, image, pixel_type)

    # writer = bioformats.OMETiffWriter()
    # writer.setTileSizeX(tile_size[0])
    # writer.setTileSizeY(tile_size[1])
    # writer.setId(filename)
    # writer.saveBytes(tile_bytes)


def conversion_test(infilename, outpath):
    javabridge.start_vm(class_path=bioformats.JARS)
    export_list = [
        (export_vips, 'tiff', ('JPEG', 90)),
        (export_bioformats, 'tiff', ('JPEG', 90)),
        (export_tiffwriter, 'tiff', ('JPEG', 90)),
        (export_tiffwriter, 'tiff', ('JPEG2000', 70)),
        (export_tiffwriter, 'tiff', ('JPEGXR', 90)),
    ]
    tile_size = (256, 256)
    image = imread(infilename)
    print(tiff_info_short(infilename))
    for export in export_list:
        function, format, compression = export
        if isinstance(compression, tuple):
            compressions = "_".join(map(str, compression))
        else:
            compressions = compression
        filename = f'{function.__name__}_{compressions}.{format}'
        outfilename = os.path.join(outpath, filename)
        function(outfilename, image, tile_size, compression)
        eimage = imread(outfilename)
        print(tiff_info_short(outfilename))
        compare_image(image, eimage)

    javabridge.kill_vm()
