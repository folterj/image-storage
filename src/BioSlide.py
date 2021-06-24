import random
import javabridge
import bioformats
from tqdm import tqdm

from src.image_util import show_image


class BioSlide:
    def __init__(self, filename):
        self.reader: bioformats.ImageReader
        self.indexes = []
        self.sizes = []
        self.mags = []
        xml = bioformats.get_omexml_metadata(filename)
        self.meta = bioformats.OMEXML(xml)
        # get magnification
        #meta.Objective()...
        for i in range(self.meta.get_image_count()):
            imeta = self.meta.image(i)
            pmeta = imeta.Pixels
            name = imeta.Name
            if pmeta.PhysicalSizeX is not None and name.endswith('x'):
                self.indexes.append(i)
                self.sizes.append((pmeta.SizeX, pmeta.SizeY))
                self.mags.append(int(name[0:-1]))
        self.reader = bioformats.ImageReader(filename)

    def read(self, args):
        image = self.reader.read(series=self.indexes[-1], XYWH=args)
        return image

    def close(self):
        self.reader.close()


if __name__ == '__main__':
    filename = 'D:/Personal/Crick/oRAScle i2i pathology/Oympus/CG_20210609_U_PEA_111_M_L_4_01.vsi'

    javabridge.start_vm(class_path=bioformats.JARS)

    slide = BioSlide(filename)
    size = slide.sizes[-1]
    xywh = (size[0]/2, size[1]/2, 512, 512)

    for i in tqdm(range(1000)):
        xywh = (random.randrange(size[0]-512), random.randrange(size[1]-512), 512, 512)
        image = slide.read(xywh)
        #show_image(image)
    slide.close()

    javabridge.kill_vm()
