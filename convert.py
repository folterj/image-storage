from src.conversion import convert_slides_tiff_select


if __name__ == '__main__':
    #input_path = 'resources/images/'
    input_path = '/camp/stp/babs/outputs/ddt/amy.strange/philip.east/histo_slides/'
    output_path = '/camp/stp/ddt/working/orascle/resources/images/'
    slidelist_filename = 'resources/csv/RAS84_classes_DX_slide_files.txt'

    #infilename = os.path.join(input_path, '4c88d448-6264-4d4b-9c4e-b04da3f65841/TCGA-69-7765-01Z-00-DX1.ac389366-febb-488c-9190-fe00bc07cd20.svs')
    #outfilename = os.path.join(output_path, '4c88d448-6264-4d4b-9c4e-b04da3f65841/TCGA-69-7765-01Z-00-DX1.ac389366-febb-488c-9190-fe00bc07cd20.tiff')
    #convert_slide_tiff(infilename, outfilename)

    convert_slides_tiff_select(input_path, '.svs', output_path, '.tiff', slidelist_filename)
