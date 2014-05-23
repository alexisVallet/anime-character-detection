""" Configuration file.
"""
import os.path

# Data folders
datarootfolder = "chardetect-data"
# images
imagesrootfolder = os.path.join(datarootfolder, "images")
imagesfolder = os.path.join(imagesrootfolder, "source")
negativesfolder = os.path.join(imagesrootfolder, "negatives")
# json
jsonfolder = os.path.join(datarootfolder, "json")
bboxesfolder = os.path.join(jsonfolder, "boundingboxes")
metadatafolder = os.path.join(jsonfolder, "metadata")
