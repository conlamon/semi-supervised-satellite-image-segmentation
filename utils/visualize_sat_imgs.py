import matplotlib.pyplot as plt
import rasterio
import numpy as np


directory = "../data/images/downloads/cairo/20170828_085947_0f3b/"
image_file = "20170828_085947_0f3b_3B_AnalyticMS.tif"

# Read in the file as a numpy array
# Note: the dimensions are weird when read in,
#       the image has dimensions C x H x W, will change this next
with rasterio.open(directory+image_file) as src:
    print("Width: {}, Height: {}".format(src.width, src.height))
    x_train = src.read()
    
# Change order to H x W x C, so that the channels are last (like normal)
x_train = np.moveaxis(x_train, 0, -1)
print("New image shape: {} -- Should have channels last".format(x_train.shape))

# Plot a single band of the image to have a look
# - Can't plot all three RGB bands at once for some reason, but single bands work
plt.imshow(x_train[:,:,0])