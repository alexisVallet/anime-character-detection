import cv2
import sys
import os
import os.path
import numpy as np
import json

class BBDrawing:
    def __init__(self, image):
        self.lbdown = False
        self.topLeft = None
        self.downRight = None
        self.srcimage = image
        self.bbs = []

    def wrapCoords(self, (x,y)):
        rows, cols = self.srcimage.shape[0:2]

        return (max(0, min(cols-1, x)),
                max(0, min(rows-1, y)))

    def draw_rectangle(self, event, x, y, flags, param):
        if self.topLeft == None and event == cv2.EVENT_LBUTTONDOWN:
            self.lbdown = True
            self.topLeft = (x,y)
        elif event == cv2.EVENT_MOUSEMOVE and self.lbdown:
            self.downRight = (x,y)
        elif event == cv2.EVENT_LBUTTONUP and self.lbdown:
            self.lbdown = False
            self.bbs.append((self.wrapCoords(self.topLeft), 
                             self.wrapCoords((x,y))))
            self.topLeft = None
            self.downRight = None

    def onKey(self,keycode):
        if keycode == ord('b') and self.bbs != []:
            self.bbs.pop()

    def getimage(self):
        # clear the image
        self.image = np.array(self.srcimage, copy=True)
        # display current rectangle if it exists
        if self.topLeft != None and self.downRight != None:
            cv2.rectangle(self.image, self.topLeft, self.downRight, (255,0,0), 1)
        # display already drawn bounding boxes
        for (tl,dr) in self.bbs:
            cv2.rectangle(self.image, tl, dr, (255,0,0), 1)
        return self.image
        
if __name__ == "__main__":
    if sys.argv < 3:
        raise ValueError("Please input 2 folder names.")
    imageFilenames = [f for f in sorted(os.listdir(sys.argv[1]), 
                                        key=lambda s: s.lower())
                      if f.endswith(('.jpg', '.png', '.gif'))]
    windowName = "Input bounding boxes for all characters"
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    
    for imageFilename in imageFilenames:
        stem = os.path.splitext(imageFilename)[0]
        print stem
        outFilename = os.path.join(sys.argv[2], stem + '_bb.json')
        # if json file already writtenm skip the image
        if os.path.isfile(outFilename):
            continue
        image = cv2.imread(os.path.join(sys.argv[1], imageFilename))
        if image == None or image.shape[0] == 0:
            print "error opening!"
            continue;
        # let the user draw the bounding boxes
        bbdrawing = BBDrawing(image)
        cv2.setMouseCallback(windowName, 
                             lambda e,x,y,f,p: bbdrawing.draw_rectangle(e,x,y,f,p))
        keycode = ord('p')

        while keycode != ord('y'):
            cv2.imshow(windowName, bbdrawing.getimage())
            keycode = cv2.waitKey(1000/60)
            bbdrawing.onKey(keycode)
        # write the bounding boxes to a json file
        outFile = open(outFilename, 'w')
        json.dump(bbdrawing.bbs, outFile)
        outFile.close()
