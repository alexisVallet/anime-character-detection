""" Configuration file.
"""
import os.path

# Data folders
datarootfolder = "chardetect-data"
imagesfolder = os.path.join(datarootfolder, "images")
jsonfolder = os.path.join(datarootfolder, "json")
bboxesfolder = os.path.join(jsonfolder, "boundingboxes")
metadatafolder = os.path.join(jsonfolder, "metadata")
negativesfolder = os.path.join(jsonfolder, "negatives")
