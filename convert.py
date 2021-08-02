from src.conversion import convert_slides_tiff_select, convert_slide_tiff, conversion_test
from src.image_util import tiff_info


def convert_slides():
    input_path = 'D:/slides'
    output_path = 'D:/slides'
    slidelist_filename = 'resources/csv/slide_list.txt'

    #convert_slide_tiff(infilename, outfilename)

    convert_slides_tiff_select(input_path, output_path, '.tiff', slidelist_filename)


if __name__ == '__main__':
    test_filename = 'D:/slides/test/test_slide.tiff'
    output_path = 'D:/slides/test/export/'

    #convert_slide_tiff(svs_filename, tiff_filename, ome=True, overwrite=True)
    #print(tiff_info(tiff_filename))
    #conversion_test(test_filename, output_path)

    convert_slides()
