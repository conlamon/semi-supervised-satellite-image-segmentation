import os, gdal, sys, rasterio
from xml.dom import minidom
import numpy as np

# File paths

TRAIN_PATH = 'train/'
TEST_PATH = 'test/'

ORIGINAL_PATH = 'original/'
NORMAL_PATH = 'normalized/'
SPLIT_256_PATH = 'split_256/'
SPLIT_512_PATH = 'split_512/'

CITY_PATH = "city/"
COAST_PATH = "coast/"
DESERT_PATH = "desert/"

TIF_PATH = "tif/"
XML_PATH = "xml/"

#ALL_PATHS = [CITY_PATH, COAST_PATH, DESERT_PATH]
ALL_PATHS = [COAST_PATH, DESERT_PATH]

tile_size_x = 256
tile_size_y = 256

tile_size_x2 = 512
tile_size_y2 = 512

for image_type in ALL_PATHS:

    # Filepaths
    RAW_TIF_PATH = TRAIN_PATH + ORIGINAL_PATH + image_type + TIF_PATH
    NORMAL_TIF_PATH = TRAIN_PATH + NORMAL_PATH + image_type
    RAW_XML_PATH = TRAIN_PATH + ORIGINAL_PATH + image_type + XML_PATH
    SAVE_256_PATH = TRAIN_PATH + SPLIT_256_PATH + image_type
    SAVE_512_PATH = TRAIN_PATH + SPLIT_512_PATH + image_type

    # Setup
    count = 0
    num_files = len([x for x in os.listdir(TRAIN_PATH + ORIGINAL_PATH + image_type + TIF_PATH) if not x == '.DS_Store'])

    # Loop through all raw tif files
    if (True):
        for filename in os.listdir(RAW_TIF_PATH):
            if not filename == '.DS_Store':

                ###########################################
                # Normalize 
                ###########################################

                # Get corresponding xml file
                xml_file = RAW_XML_PATH + filename.split(".")[0] + ".xml"

                # Load xml file
                xmldoc = minidom.parse(xml_file)
                nodes = xmldoc.getElementsByTagName("ps:bandSpecificMetadata")

                # Parse and fill coeffs
                coeffs = {}
                for node in nodes:
                    bn = node.getElementsByTagName("ps:bandNumber")[0].firstChild.data
                    if bn in ['1', '2', '3', '4']:
                        i = int(bn)
                        value = node.getElementsByTagName("ps:reflectanceCoefficient")[0].firstChild.data
                        coeffs[i] = float(value)

                # Open original tif image
                with rasterio.open(RAW_TIF_PATH + filename) as src:
                    raw_image = src.read()

                    # Get into correct shape for normalization
                    raw_image = np.rollaxis(raw_image, 0, 3)

                    # Create new image
                    normal_image = np.zeros(raw_image.shape)
                    for i in range(1):
                        normal_image[:, :, i] = raw_image[:, :, i] * coeffs[i+1]

                    # Revert to original shape
                    normal_image = np.moveaxis(normal_image, 2, 0)

                    # Save normalized tif image
                    kwargs = src.meta
                    kwargs.update(dtype=rasterio.float64)
                    with rasterio.open(NORMAL_TIF_PATH + filename, 'w', **kwargs) as dst:
                            dst.write(normal_image)

                ###########################################
                # Split 
                ###########################################

                count += 1
                print("\n\n\n[%s] Image %d / %d\n\n\n" % (image_type, count, num_files))

                ds = gdal.Open(NORMAL_TIF_PATH + filename)
                band = ds.GetRasterBand(1)
                xsize = band.XSize
                ysize = band.YSize

                # 256x256 split
                if (True):
                    for i in range(0, xsize, tile_size_x):
                        for j in range(0, ysize, tile_size_y):
                            com_string = "gdal_translate -of GTIFF -epo -srcwin " + \
                                str(i)+ ", " + str(j) + ", " + str(tile_size_x) + ", " + str(tile_size_y) + " " + \
                                str(NORMAL_TIF_PATH + filename) + " " + \
                                str(SAVE_256_PATH + filename[:-4]) + "_" + str(i) + "_" + str(j) + ".tif"
                            os.system(com_string)

                # 512x512 split
                if (False):
                    for i in range(0, xsize, tile_size_x2):
                        for j in range(0, ysize, tile_size_y2):
                            com_string = "gdal_translate -of GTIFF -epo -srcwin " + \
                                str(i)+ ", " + str(j) + ", " + str(tile_size_x2) + ", " + str(tile_size_y2) + " " + \
                                str(NORMAL_TIF_PATH + filename) + " " + \
                                str(SAVE_512_PATH + filename[:-4]) + "_" + str(i) + "_" + str(j) + ".tif"
                            os.system(com_string)

    ###########################################
    # Delete empty images 
    ###########################################
    if (True):

        # Loop through all normalized images and delete
        for filename in os.listdir(NORMAL_TIF_PATH):
            if not filename == '.DS_Store':
                print("Deleted " + filename)
                os.system("rm "+ NORMAL_TIF_PATH + filename)

        # Loop through all tiles and only keep those with non-zero values
        for filename in os.listdir(SAVE_256_PATH):
            if not filename == '.DS_Store':

                # Open file
                with rasterio.open(SAVE_256_PATH + filename) as src:
                    raw_image = src.read()

                    # Check max value in image, if 0, delete
                    max_value = np.amax(raw_image)
                    print(max_value)
                    if max_value == 0.0:
                        print("Deleted " + filename)
                        os.system("rm "+ SAVE_256_PATH + filename)
