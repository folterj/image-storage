from PIL import Image
import numpy as np
from aicsimageio import imread_dask
from aicsimageio.readers import TiffReader
from tifffile import TiffFile


class AICSImageReader:
    def __init__(self, filename):
        self.pages = []
        self.level_dimensions = {}
        tiff = TiffFile(filename)
        for index, page in enumerate(tiff.pages):
            if page.is_tiled:
                self.level_dimensions[index] = (page.imagewidth, page.imagelength)
        reader = TiffReader(filename)
        dims = reader.dims
        shape = reader.shape
        lazy = imread_dask(filename)
        #test = lazy[0,0,0,0:10,0:10,:]
        #test.compute()
        test = reader.dask_data[0:300, 0:300, :].compute()
        result = reader.get_image_dask_data(reader.dims, S=0, Y=0, X=0)
        result


    def get_thumbnail(self, size):
        level = len(self.level_dimensions) - 1
        tile = self.read_region((0, 0), level, self.level_dimensions[level])
        thumb = Image.fromarray(tile)
        thumb.thumbnail(size, Image.ANTIALIAS)
        return thumb

    def read_region(self, position, level, size):
        x=0