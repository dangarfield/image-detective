from __future__ import (absolute_import, division, print_function)
from PIL import Image
import six
import imagehash

def get_hash_method(hashmethod):
    if hashmethod == 'ahash':
        hashfunc = imagehash.average_hash
    elif hashmethod == 'phash':
        hashfunc = imagehash.phash
    elif hashmethod == 'dhash':
        hashfunc = imagehash.dhash
    elif hashmethod == 'whash-haar':
        hashfunc = imagehash.whash
    elif hashmethod == 'whash-db4':
        hashfunc = lambda img: imagehash.whash(img, mode='db4')
    else:
        hashfunc = ''
    return hashfunc

def generate_hashes_for_image(imgPath):

    print ("Generating hash for: " + imgPath)
    img = Image.open(imgPath)

    data = {}
    data['ahash'] = imagehash.average_hash(img, hash_size=8)
    data['phash'] = imagehash.phash(img, hash_size=8)
    data['dhash'] = imagehash.dhash(img, hash_size=8)
    data['whash'] = imagehash.whash(img, hash_size=8)
    data['whashDb4'] = imagehash.whash(img, mode='db4')
    #print (data)
    return data

def find_similar_images(userpath, hashfunc=imagehash.average_hash):
    import os

    def is_image(filename):
        f = filename.lower()
        return f.endswith(".png") or f.endswith(".jpg") or \
            f.endswith(".jpeg") or f.endswith(".bmp") or f.endswith(".gif")

    image_filenames = [os.path.join(userpath, path)
                       for path in os.listdir(userpath) if is_image(path)]

    #print (image_filenames)
    #print(image_filenames)

    images = {}
    for img in sorted(image_filenames):
        hash = hashfunc(Image.open(img))
        print (hash)
        images[hash] = images.get(hash, []) + [img]
        
    print (images)

    matches = []
    for k, img_list in six.iteritems(images):
        if len(img_list) > 1:
            matches.append(img_list)
            #print(" ".join(img_list))
    #print (matches)
    return matches