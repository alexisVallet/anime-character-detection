""" Unit tests for negatives.py.
"""
import negatives as neg
import unittest
import acdconf as conf
import cv2
import os
import os.path
import json

class TestNegatives(unittest.TestCase):
    def test_negative_samples(self):
        imagefilenames = [f for f in sorted(os.listdir(conf.imagesfolder), 
                                            key=str.lower) 
                          if f.endswith('.jpg')]

        for imagefilename in imagefilenames:
            print "processing " + imagefilename
            # Load image and bounding boxes
            image = cv2.imread(os.path.join(conf.imagesfolder, imagefilename))
            stem = os.path.splitext(imagefilename)[0]
            bboxesfile = open(os.path.join(conf.bboxesfolder, stem + '_bb.json'))
            bboxes = json.load(bboxesfile)
            bboxesfile.close()
            # Compute the negatives, and write the boxes info to the output folder
            negatives = neg.negative_samples(image, bboxes)
            # First checks whether the negatives are indeed only background
            andf = lambda b1, b2: b1 and b2
            # Check that the negatives are indeed background
            onlybg = reduce(andf, map(lambda negval: reduce(andf, map(lambda bbox: not neg.overlapping(bbox, negval), bboxes)), negatives), True)
            # If test fails, show debug info before assertion
            if not onlybg:
                for [ul,dr] in bboxes:
                    cv2.rectangle(image, tuple(ul), tuple(dr), (255,0,0), 1)
                cv2.imshow("image", image)
                i = 0
                for negative in negatives:
                    [[x1,y1],[x2,y2]] = negative
                    cv2.imshow("negative " + repr(i), image[y1:y2,x1:x2,:])
                    i += 1
                cv2.waitKey(0)
            self.assertTrue(onlybg)

if __name__ == '__main__':
    unittest.main()
