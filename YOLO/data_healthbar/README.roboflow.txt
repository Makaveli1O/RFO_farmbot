
RFO caliana - v8 2023-02-21 8:00pm
==============================

This dataset was exported via roboflow.com on February 21, 2023 at 7:01 PM GMT

Roboflow is an end-to-end computer vision platform that helps you
* collaborate with your team on computer vision projects
* collect & organize images
* understand and search unstructured image data
* annotate, and create datasets
* export, train, and deploy computer vision models
* use active learning to improve your dataset over time

For state of the art Computer Vision training notebooks you can use with this dataset,
visit https://github.com/roboflow/notebooks

To find over 100k other datasets and pre-trained models, visit https://universe.roboflow.com

The dataset includes 833 images.
Game-mob are annotated in YOLOv8 format.

The following pre-processing was applied to each image:
* Auto-orientation of pixel data (with EXIF-orientation stripping)
* Resize to 416x416 (Fit (white edges))
* Auto-contrast via adaptive equalization

The following augmentation was applied to create 3 versions of each source image:
* Random brigthness adjustment of between -36 and +36 percent

The following transformations were applied to the bounding boxes of each image:
* Random brigthness adjustment of between -34 and +34 percent


