import os
import numpy as np
import random
from omero.gateway import BlitzGateway
from getpass import getpass
from tifffile import TiffWriter
from tqdm import tqdm

from src.image_util import show_image


SRC_HOST = 'ssl://omero-prod.camp.thecrick.org'


class Omero:
    def __init__(self):
        self.connected = False

    def connect_prompt(self):
        self.connect(SRC_HOST, input('Username: '), getpass('OMERO Password: '))
        self.conn.SERVICE_OPTS.setOmeroGroup('-1')
        print(f'Connected as {self.conn.getUser().getName()}')

    def connect(self, hostname, username, password):
        """
        Connect to an OMERO server
        :param hostname: Host name
        :param username: User
        :param password: Password
        :return: Connected BlitzGateway
        """
        self.conn = BlitzGateway(username, password,
                            host=hostname, secure=True)
        self.conn.connect()
        if not self.conn.isConnected():
            self.disconnect()
            raise ConnectionError
        self.conn.c.enableKeepAlive(60)
        self.connected = True

    def disconnect(self):
        self.conn.close()
        self.connected = False

    def list_projects(self):
        projects = self.conn.listProjects()      # may include other users' data
        for project in projects:
            print_omero_object(project)

    def open_dataset(self, project_name, dataset_name):
        self.project = self.conn.getObject('Project', project_name)
        self.dataset = self.project.findChildByName(dataset_name)
        return self.dataset

    def get_size(self, image_object):
        xs, ys = image_object.getSizeX(), image_object.getSizeY()
        zs, cs, ts = image_object.getSizeZ(), image_object.getSizeC(), image_object.getSizeT()
        return xs, ys, zs, cs, ts

    def get_metadata(self, image_object):
        metadata = {}
        data = []
        for data0 in image_object.loadOriginalMetadata():
            if data0 is not None:
                data += data0
        for key, value in data:
            keys = key.split('|')
            self.add_dict_tree(metadata, keys, value)
        return metadata

    def add_dict_tree(self, metadata, keys, value):
        key = keys[0]
        if len(keys) > 1:
            if key not in metadata:
                metadata[key] = {}
            self.add_dict_tree(metadata[key], keys[1:], value)
        else:
            metadata[key] = value

    def get_magnification(self, image_object):
        return image_object.getObjectiveSettings().getObjective().getNominalMagnification()

    def convert_slide_to_tiff(self, image_id, outfilename):
        image_object = self.dataset.findChildByName(image_id)
        # image_object = self.conn.getObject("Image", image_id)
        w, h, zs, cs, ts = self.get_size(image_object)
        print('Size:', w, h, zs, cs, ts)

        #tiff_content = image_object.exportOmeTiff()    # not working
        #with open(outfilename, 'wb') as writer:
        #    writer.write(tiff_content)

        # slide_image = pixels.getPlane()   # not working

        h//=100
        w//=100
        read_size = 1024
        ny = int(np.ceil(h / read_size))
        nx = int(np.ceil(w / read_size))
        tile_size = (256, 256)

        metadata = self.get_metadata(image_object)
        # convert to summary for page description?
        description = f'AppMag = {self.get_magnification(image_object)}'
        pixels = image_object.getPrimaryPixels()

        slide_image = np.zeros((h, w, cs), dtype=np.uint8)

        for y in range(ny):
            for x in range(nx):
                sx, sy = x * read_size, y * read_size
                tw, th = read_size, read_size
                if sx + tw > w:
                    tw = w - sx
                if sy + th > h:
                    th = h - sy
                xywh = (sx, sy, tw, th)
                tile_coords = [(0, c, 0, xywh) for c in range(cs)]
                image_gen = pixels.getTiles(tile_coords)
                for c, image in enumerate(image_gen):
                    slide_image[sy:sy + th, sx:sx + tw, c] = image

        outpath = os.path.dirname(outfilename)
        if not os.path.exists(outpath):
            os.makedirs(outpath)

        with TiffWriter(outfilename, bigtiff=True, ome=True) as writer:
            writer.write(slide_image, photometric='RGB', tile=tile_size, compression='JPEG',
                         metadata=metadata)

    def random_read_test(self):
        print('Read test')
        image_objects = []
        sizes = []
        pixel_objects = []
        for image_object in self.dataset.listChildren():
            name = image_object.getName()
            if not name.endswith('_label') and not name.endswith('_macro'):
                size = image_object.getSizeX(), image_object.getSizeY()
                nchannels = image_object.getSizeC()
                print(name, size)
                pixels = image_object.getPrimaryPixels()
                image_objects.append(image_object)
                sizes.append(size)
                pixel_objects.append(pixels)

        for _ in tqdm(range(100)):
            i = random.randrange(len(image_objects))
            size = sizes[i]
            pixels = pixel_objects[i]
            w = 512
            h = 512
            xywh = (size[0]/2, size[1]/2, 512, 512)

            xywh = (random.randrange(size[0]-512), random.randrange(size[1]-512), 512, 512)
            tile_coords = [(0, c, 0, xywh) for c in range(nchannels)]
            image_gen = pixels.getTiles(tile_coords)
            dest_image = np.zeros((h, w, nchannels), dtype=np.uint8)
            for c, image in enumerate(image_gen):
                dest_image[:, :, c] = image
            show_image(dest_image)

def print_omero_object(object, indent=0):
    """
    Helper method to display info about OMERO objects.
    Not all objects will have a "name" or owner field.
    """
    print("""%s%s:%s  Name:"%s" (owner=%s)""" % (
        " " * indent,
        object.OMERO_CLASS,
        object.getId(),
        object.getName(),
        object.getOwnerOmeName()))

    for child in object.listChildren():
        print('\t', child.getName())


if __name__ == '__main__':
    omero = Omero()
    omero.connect_prompt()

    #omero.open_dataset(61, 'Histology Tiffs')
    omero.open_dataset(355, 'K021')
    print_omero_object(omero.dataset)

    #omero.random_read_test()

    image_id = 'K021_PR001'
    omero.convert_slide_to_tiff(image_id, '../resources/images/test.tiff')

    omero.disconnect()
