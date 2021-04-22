import numpy as np
from PIL import Image
from tifffile import TiffFile


# https://pypi.org/project/tifffile/
# based on https://gist.github.com/rfezzani/b4b8852c5a48a901c1e94e09feb34743


class TiffSlide:
    def __init__(self, filename, executor):
        self.executor = executor
        self.pages = []
        self.level_dimensions = []
        self.tiff = TiffFile(filename, is_ome=True)
        for page in self.tiff.pages:
            if page.is_tiled:
                self.pages.append(page)
                self.level_dimensions.append((page.imagewidth, page.imagelength))

    def get_thumbnail(self, size):
        thumb = Image.fromarray(self.pages[-1].asarray())
        thumb.thumbnail(size, Image.ANTIALIAS)
        return thumb

    def asarray(self, level, x0, y0, x1, y1):
        # based on tiffile asarray
        dw = x1 - x0
        dh = y1 - y0
        page = self.pages[level]
        fh = page.parent.filehandle

        tile_width, tile_height = page.tilewidth, page.tilelength
        tile_y0, tile_x0 = y0 // tile_height, x0 // tile_width
        tile_y1, tile_x1 = np.ceil([y1 / tile_height, x1 / tile_width]).astype(int)
        nx = tile_x1 - tile_x0
        ny = tile_y1 - tile_y0
        w = (tile_x1 - tile_x0) * tile_width
        h = (tile_y1 - tile_y0) * tile_height
        tile_per_line = int(np.ceil(page.imagewidth / tile_width))
        dataoffsets = []
        databytecounts = []
        for y in range(tile_y0, tile_y1):
            for x in range(tile_x0, tile_x1):
                index = int(y * tile_per_line + x)
                if index < len(page.databytecounts):
                    dataoffsets.append(page.dataoffsets[index])
                    databytecounts.append(page.databytecounts[index])

        out = np.zeros((h, w, 3), page.dtype)

        def process_decoded(decoded, out=out):
            segment, indices, shape = decoded
            index = indices[-2] // shape[-2]
            y = index // nx
            x = index % nx

            im_y = y * tile_height
            im_x = x * tile_width
            out[im_y: im_y + tile_height, im_x: im_x + tile_width, :] = segment[0]

        for _ in self.segments(
                func=process_decoded,
                lock=fh.lock,
                sort=True,
                page=page,
                dataoffsets=dataoffsets,
                databytecounts=databytecounts
        ):
            pass

        im_y0 = y0 - tile_y0 * tile_height
        im_x0 = x0 - tile_x0 * tile_width
        return out[im_y0: im_y0 + dh, im_x0: im_x0 + dw, :]

    def segments(self, lock, func, sort, page, dataoffsets, databytecounts):
        # based on tiffile segments
        fh = page.parent.filehandle

        def decode(args, page=page, func=func):
            if page.jpegtables is not None:
                decoded = page.decode(*args, page.jpegtables)
            else:
                decoded = page.decode(*args)
            return func(decoded)

        for segments in fh.read_segments(
                dataoffsets,
                databytecounts,
                lock=lock,
                sort=sort,
                flat=False,
        ):
            yield from self.executor.map(decode, segments)