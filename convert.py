from src.Omero import Omero, print_omero_object
from src.conversion import convert_slides_tiff_select, convert_slide_tiff, conversion_test
from src.image_util import tiff_info


def convert_slides():
    #input_path = 'resources/images/'
    input_path = 'D:/Personal/Crick/oRAScle i2i pathology/slides'
    #input_path = '/camp/stp/babs/outputs/ddt/amy.strange/philip.east/histo_slides/'
    output_path = 'D:/Personal/Crick/oRAScle i2i pathology/slides'
    #output_path = '/camp/stp/ddt/working/orascle/resources/images/'
    slidelist_filename = 'resources/csv/RAS84_classes_DX_slide_files.txt'

    #infilename = os.path.join(input_path, '4c88d448-6264-4d4b-9c4e-b04da3f65841/TCGA-69-7765-01Z-00-DX1.ac389366-febb-488c-9190-fe00bc07cd20.svs')
    #outfilename = os.path.join(output_path, '4c88d448-6264-4d4b-9c4e-b04da3f65841/TCGA-69-7765-01Z-00-DX1.ac389366-febb-488c-9190-fe00bc07cd20.tiff')
    #convert_slide_tiff(infilename, outfilename)

    convert_slides_tiff_select(input_path, output_path, '.tiff', slidelist_filename)


def convert_omero_slides():
    omero = Omero()
    omero.connect_prompt()

    #omero.open_dataset(61, 'Histology Tiffs')
    omero.open_dataset(355, 'K021')
    print_omero_object(omero.dataset)

    #omero.random_read_test()

    image_id = 'K021_PR001'
    omero.convert_slide_to_tiff(image_id, 'resources/images/test.tiff')

    omero.disconnect()


if __name__ == '__main__':
    svs_filename = 'D:/Personal/Crick/oRAScle i2i pathology/slides/2e405d74-1bf4-4b86-9b69-7f85774e5cad/TCGA-05-5425-01Z-00-DX1.85865B2F-4888-43DD-A501-458BEFCF832B.svs'
    tiff_filename = 'D:/Personal/Crick/oRAScle i2i pathology/slides/2e405d74-1bf4-4b86-9b69-7f85774e5cad/test.tiff'

    test_filename = 'D:/Personal/Crick/oRAScle i2i pathology/slides/test/test_slide.tiff'
    output_path = 'D:/Personal/Crick/oRAScle i2i pathology/slides/test/export/'

    #convert_slide_tiff(svs_filename, tiff_filename, ome=True, overwrite=True)
    #print(tiff_info(tiff_filename))
    conversion_test(test_filename, output_path)

    #convert_slides()
    #convert_omero_slides()
