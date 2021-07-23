import os
import random
from omero.gateway import BlitzGateway
from getpass import getpass
from tifffile import TiffWriter
from tqdm import tqdm


SRC_HOST = 'ssl://omero-prod.camp.thecrick.org'


class Omero:
    def __init__(self):
        self.connected = False

    def connect_prompt(self):
        self.connect(SRC_HOST, input("Username: "), getpass("OMERO Password: "))
        self.conn.SERVICE_OPTS.setOmeroGroup('-1')
        print("Connected as {}".format(self.conn.getUser().getName()))

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
        ws, hs = image_object.getSizeX(), image_object.getSizeY()
        zs, cs, ts = image_object.getSizeZ(), image_object.getSizeC(), image_object.getSizeT()
        return ws, hs, zs, cs, ts

    def convert_slide_to_tiff(self, image_id, outfilename):
        image_object = self.dataset.findChildByName(image_id)
        # image_object = self.conn.getObject("Image", image_id)
        ws, hs, zs, cs, ts = self.get_size(image_object)
        print('Size:', ws, hs, zs, cs, ts)

        tiff_content = image_object.exportOmeTiff()
        with open(outfilename, 'wb') as writer:
            writer.write(tiff_content)

        # outpath = os.path.dirname(outfilename)
        # if not os.path.exists(outpath):
        #     os.makedirs(outpath)
        # pixels = image_object.getPrimaryPixels()
        # with TiffWriter(outfilename, bigtiff=True) as writer:
        #     for z in zs:
        #         tile_size = (tilelength, tilewidth)
        #         slide_image = pixels.getPlane(z, 0, 0)
        #         writer.write(slide_image, tile=tile_size, compression='JPEG', description=page.description)

    def random_read_test(self):
        print('Read test')
        image_objects = []
        sizes = []
        pixel_objects = []
        for image_object in self.dataset.listChildren():
            name = image_object.getName()
            if not name.endswith('_label') and not name.endswith('_macro'):
                size = image_object.getSizeX(), image_object.getSizeY()
                print(name, size)
                pixels = image_object.getPrimaryPixels()
                image_objects.append(image_object)
                sizes.append(size)
                pixel_objects.append(pixels)

        for _ in tqdm(range(100)):
            i = random.randrange(len(image_objects))
            size = sizes[i]
            pixels = pixel_objects[i]
            xywh = (size[0]/2, size[1]/2, 512, 512)

            xywh = (random.randrange(size[0]-512), random.randrange(size[1]-512), 512, 512)
            tile_coords = [(0, 0, 0, xywh)]
            image_gen = pixels.getTiles(tile_coords)
            for image in image_gen:
                image.shape
                #show_image(image)

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
    slide_image = omero.convert_slide_to_tiff(image_id, '../resources/images/test.tiff')

    omero.disconnect()
