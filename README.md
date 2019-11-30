# Semi-supervised Image Segmentation of Satellite Imagery

Utilized a [U-Net](https://arxiv.org/abs/1505.04597) to perform segmentation of buildings in satellite imagery. Pre-trained the U-Net in a semi-supervised fashion by changing the last layer and training it as an autoencoder. Then switched last layer back to normal and trained on labelled data to perform the segmentation. Poster with results can be seen [here](http://bit.ly/2ys9X3T).
