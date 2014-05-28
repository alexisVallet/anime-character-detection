""" Generates random folds for k-fold cross validation from a given dataset.
    Actually splits the positive samples, then takes generated negative samples 
    from the chosen positive ones ONLY. This is important, as negatives from other
    folds may end up in the test data at some point.
"""
import sys
import os
import os.path
import numpy as np
import math

if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise ValueError("""
Please give a number of folds, input positive and negative folders, 
and an output folder.""");
    k = int(sys.argv[1]) # yeah I know I know
    if k < 2:
        raise ValueError("The number of folds must be at least 2.")
    posfolder = sys.argv[2]
    negfolder = sys.argv[3]
    outfolder = sys.argv[4]
    # Create the output subfolders if they don't already exist
    for i in range(0,k):
        try:
            # Create one folder for positives and negatives separately
            os.makedirs(os.path.join(outfolder, repr(i), 'positives'))
            os.makedirs(os.path.join(outfolder, repr(i), 'negatives'))
        except OSError:
            # makedirs throws an OSError when the folder already exists
            pass
    # Compute a random permutation of all the image files in the positive folder
    imagenames = [f for f in os.listdir(posfolder) 
                  if f.endswith(('.jpg','.png', '.gif'))]
    perm = np.random.permutation(len(imagenames))
    permutednames = [imagenames[i] for i in perm]
    # Compute the size of each slice.
    minfoldsize = int(math.floor(len(imagenames) / k))
    remainder = len(imagenames) - k * minfoldsize
    foldsizes = [minfoldsize] * k
    # Just add 1 to the remainder first folds.
    for i in range(0,remainder):
        foldsizes[i] = foldsizes[i] + 1
    # Fill up the folds.
    foldidx = 0
    idx = 0
    for foldsize in foldsizes:
        # For each image in the fold, create a symlink in the folder to avoid
        # copying data.
        posoutfolder = os.path.join(outfolder, repr(foldidx), 'positives')
        negoutfolder = os.path.join(outfolder, repr(foldidx), 'negatives')
        for imgname in permutednames[idx:idx+foldsize]:
            # Carefully make the symlink with a relative path, so it plays well with git
            posinpath = os.path.relpath(os.path.join(posfolder, imgname), posoutfolder)
            possymlinkpath = os.path.join(posoutfolder, imgname)
            if not os.path.isfile(possymlinkpath):
                os.symlink(posinpath, possymlinkpath)
            # Now similarly make symlinks to negative samples
            posstem = os.path.splitext(imgname)[0]
            negativefiles = [f for f in os.listdir(negfolder)
                             if f.startswith(posstem + '_')]
            for negativefile in negativefiles:
                negimpath = os.path.relpath(os.path.join(negfolder, negativefile),
                                            negoutfolder)
                negsymlinkpath = os.path.join(negoutfolder, negativefile)
                if not os.path.isfile(negsymlinkpath):
                    os.symlink(negimpath, negsymlinkpath)
        idx = idx + foldsize
        foldidx = foldidx + 1
