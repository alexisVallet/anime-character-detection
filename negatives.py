""" Script for generating negative samples out of positive ones, taking the largest
possible background patches.
"""
import cv2
import json
import os.path
import os
import sys

def boxArea(bbox):
    """ Returns the area of a bounding box, assuming it is well formed.
    """
    [[ulx,uly], [drx,dry]] = bbox

    return (drx - ulx) * (dry - uly)

def overlapping(bbox1, bbox2):
    [[ulx1, uly1],[drx1,dry1]] = bbox1
    [[ulx2, uly2],[drx2,dry2]] = bbox2
    return not (ulx1 > drx2 or ulx2 > drx1 or uly1 > dry2 or uly2 > dry1)

def nonEmptyAndWellFormed(bbox):
    [[ulx,uly],[drx,dry]] = bbox
    return boxArea(bbox) > 0 and ulx < drx and uly < dry

def divide(bigbox, smallbox):
    [[ulx1, uly1],[drx1,dry1]] = bigbox
    [[ulx2, uly2],[drx2,dry2]] = smallbox
    w = drx1 - ulx1
    h = dry1 - uly1
    bw = drx2 - ulx2
    bh = dry2 - uly2

    a, b, c, d = [None] * 4
    # If the box is higher than it is wide compared to the image size, cut horizontally
    if float(bw) / float(w) < float(bh) / float(h):
        a = [[ulx1,uly1],[ulx2-1,dry1]]
        b = [[drx2+1,uly1],[drx1,dry1]]
        c = [[ulx2,dry2+1],[drx2,dry1]]
        d = [[ulx2,uly1],[drx2,uly2-1]]
    else: # Otherwise cut vertically
        a = [[ulx1,uly1],[drx1,uly2-1]]
        b = [[ulx1,dry2+1],[drx1,dry1]]
        c = [[drx2+1,uly2],[drx1,dry2]]
        d = [[ulx1,uly2],[ulx2-1,dry2]]
    # Filter out empty boxes or malformed boxes - happen when smallbox is not contained
    # within bigbox.

    return filter(nonEmptyAndWellFormed, [a,b,c,d])

def negative_sample_boxes(imagebox, bboxes):
    """ Computes negative sample boxes covering the entire image not including the
        specified bounding boxes. The returned samples are optimal in the sense that
        they are the biggest possible rectangles (at least I think, not proved yet).
        Assumes the bounding boxes to be sorted in decreasing order of area. Runs in
        O(nlog(n)) where n is the number of bounding boxes.
    """
    overlapbb = filter(lambda bb: overlapping(imagebox, bb), bboxes)
    # If there are no overlapping bounding boxes, the image contains only background 
    # and is a valid negative sample.
    if overlapbb == []:
        return [imagebox]
    # Otherwise, we divide the image around the largest box
    else:
        divisions = divide(imagebox, overlapbb[0])
        smallerBoxes = overlapbb[1:]
        negatives = []
        
        # Call the algorithm recursively on each division
        for division in divisions:
            negatives += negative_sample_boxes(division, smallerBoxes)
        return negatives

def negative_samples(image, bboxes):
    rows, cols = image.shape[0:2]
    imagebox = [[0,0],[cols-1,rows-1]]
    sortedboxes = sorted(bboxes, key=boxArea, reverse=True)
    negativeboxes = negative_sample_boxes(imagebox, sortedboxes)
    
    return negativeboxes

if __name__ == "__main__":
    if sys.argv < 4:
        raise ValueError("Please enter 3 folder names")
    imagefilenames = [f for f in sorted(os.listdir(sys.argv[1]), key=str.lower) 
                      if f.endswith('.jpg')]

    for imagefilename in imagefilenames:
        print "processing " + imagefilename
        # Load image and bounding boxes
        image = cv2.imread(os.path.join(sys.argv[1], imagefilename))
        stem = os.path.splitext(imagefilename)[0]
        bboxesfile = open(os.path.join(sys.argv[2], stem + '_bb.json'))
        bboxes = json.load(bboxesfile)
        bboxesfile.close()
        # Compute the negatives, and write the boxes info to the output folder
        negatives = negative_samples(image, bboxes)
        # First checks whether the negatives are indeed only background
        andf = lambda b1, b2: b1 and b2
        # Check that the negatives are indeed background
        onlybg = reduce(andf, map(lambda neg: reduce(andf, map(lambda bbox: not overlapping(bbox, neg), bboxes)), negatives), True)
        if not onlybg:
            cv2.imshow("image", image)
            i = 0
            for negative in negatives:
                [[x1,y1],[x2,y2]] = negative
                cv2.imshow("negative " + repr(i), image[y1:y2,x1:x2,:])
            cv2.waitKey(0)
        outputFile = open(os.path.join(sys.argv[3], stem + '_neg.json'), 'w')
        json.dump(negatives, outputFile)
        outputFile.close()
