import os

from src.conversion import tiff_convert


if __name__ == '__main__':
    image_dir = 'resources/images/'
    infilename = os.path.join(image_dir, '4c88d448-6264-4d4b-9c4e-b04da3f65841/TCGA-69-7765-01Z-00-DX1.ac389366-febb-488c-9190-fe00bc07cd20.svs')
    outfilename = os.path.join(image_dir, '4c88d448-6264-4d4b-9c4e-b04da3f65841/TCGA-69-7765-01Z-00-DX1.ac389366-febb-488c-9190-fe00bc07cd20.tiff')

    tiff_convert(infilename, outfilename)
