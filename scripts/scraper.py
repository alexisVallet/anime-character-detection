""" Scraper of images for deviantArt's RSS feed.
"""
import cv2
import feedparser as fp
import re
import urllib
import requests
import json
import os.path

def fanartScraper(searchString, nbImages, sortBy, outputFolder):
    """ Scrapes fanart images out of deviantArt, writing them to a specific folder.
        Also puts all the metadata into a json file for future usage.
    Args:
        searchString (str): search query to submit to deviantArt.
        nbImages (int): number of images to scrape.
        sortBy (str): string specifying how deviantArt sorts the results. Can be:
            'popular'
        outputFolder (str): folder to write the images and json info files to.
    Raises:
        ValueError: when nbImages is greater than the number of images returned by the
            feed.
        RuntimeError: when the rss feed provides unexpected data.
    """
    rssUrl = ('http://backend.deviantart.com/rss.xml?type=deviation&q='
              + urllib.quote_plus('boost:' + sortBy + ' ' + searchString + ' in:fanart/manga'))
    feed = fp.parse(rssUrl)
    
    # Then scrape each entry individually into image and json files.
    if len(feed.entries) < nbImages:
        raise ValueError("Cannot scrape " + nbImages 
                         + " because the feed only contains " + len(feed.entries))
    # Set the base filename for both json and image files
    baseFilename = reduce(lambda word, rest: word + '_' + rest,
                          re.sub("[^\w]", " ", searchString).split())
    currentImageIdx = 0
    currentEntryIdx = 0

    while currentImageIdx < nbImages and currentEntryIdx < len(feed.entries):
        filename = baseFilename + '_' + repr(currentImageIdx)
        fileStem = os.path.join(outputFolder, filename)
        jsonFilename = fileStem + '.json'
        if (os.path.isfile(fileStem + '.jpg') 
            or os.path.isfile(fileStem + '.png')
            or os.path.isfile(fileStem + '.gif')
            or os.path.isfile(fileStem + '.svg')):
            currentImageIdx += 1
            currentEntryIdx += 1
            continue
        currentEntry = feed.entries[currentEntryIdx]
        # First check that the image url has the right mime type 
        resp = requests.get(currentEntry.media_content[0]['url'])
        fileExtension = None
        contentType = resp.headers['content-type']
        typeToExt = {
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/svg+xml': 'svg'
            }
        try:
            fileExtension = typeToExt[contentType]
        except KeyError:
            raise RuntimeError("The url specified by the field for " + filename 
                               + " is not an image.")
        # Display the image and ask the user whether it's the right character
        # Can't think of an easy way to load the binary data straight into opencv, so
        # I first write it to a file which is then deleted if it's not the right char.
        imageFilename = os.path.join(outputFolder, filename + '.' + fileExtension)
        urllib.urlretrieve(currentEntry.media_content[0]['url'],imageFilename)
        image = cv2.imread(imageFilename)
        pressedKey = -1
        yesCode = ord('y')
        noCode = ord('n')
        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        
        while pressedKey != yesCode and pressedKey != noCode:
            try:
                cv2.imshow("image", image)
                pressedKey = cv2.waitKey(0)
            except:
                print "image cannot be displayed"
                currentImageIdx += 1
                currentEntryIdx += 1
                pressedKey = noCode
        if pressedKey == yesCode:
            # Write the entire entry to a json file for exhaustiveness
            jsonFile = open(jsonFilename, 'w')
            json.dump(currentEntry, jsonFile, indent = 4, default = repr)
            jsonFile.close()
            currentImageIdx += 1
        else:
            os.remove(imageFilename)
        currentEntryIdx += 1

if __name__ == "__main__":
    characterNames = [
        'asuka langley',
        'rei ayanami',
        'miku hatsune',
        'monkey d luffy',
        'roronoa zoro',
        'uzumaki naruto',
        'sakura haruno',
        'phoenix wright',
        'maya fey',
        'suzumiya haruhi',
        'asahina mikuru',
        'ginko',
        'yu narukami',
        'naoto shirogane',
        'shigeru akagi',
        'kaiji',
        'lain',
        'faye valentine',
        'radical edward',
        'motoko kusanagi'
        ]
    
    for name in characterNames:
        print "scraping images for " + name + "..."
        fanartScraper(name, 50, 'popular', os.path.join('..', 'chardetect', 'images'))
